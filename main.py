import asyncio
import logging
import re
from typing import Callable
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, Tag
from fastapi import FastAPI

from ai.prompt import Prompt
from ai.llm import Llm
from constants import *
from dtypes.news_dict import NewsDict
from dtypes.selector import Selector
from protos import source_pb2_grpc
from protos.news_pb2 import NewsAddRequest
from utils.infinite_scrolling_iterator import InfiniteScrollIterator
from utils.pagination_iterator import PaginationIterator
from utils.utils import contains_triggers
from dtypes.author import Author
from settings import *
from utils.custom_driver import CustomDriver
from concurrent.futures import ThreadPoolExecutor
import grpc
from services.source_service import SourceService
from settings import GRPC_ADDRESS
import logging
from utils.trigger_file import TriggerFile
from time import sleep
import time
from config.db import DatabaseConfig
from repositories.source_repository import SourceRepository


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)
llm = Llm()

app = FastAPI(
    title="Africa-AI-Insight-Scraper",
    description="Web scraper for AI and Africa-related content",
    version="1.0.0",
)

try:
    ai_trigger_words = TriggerFile(AI_TRIGGER_WORDS_PATH)
    ai_trigger_phrases = TriggerFile(AI_TRIGGER_PHRASES_PATH)
    africa_trigger_words = TriggerFile(AFRICA_TRIGGER_WORDS_PATH)
    africa_trigger_phrases = TriggerFile(AFRICA_TRIGGER_PHRASES_PATH)

    trigger_words_ai = ai_trigger_words.get()
    logger.info(f"Loaded {len(trigger_words_ai)} AI trigger words")

    trigger_phrases_ai = ai_trigger_phrases.get()
    logger.info(f"Loaded {len(trigger_phrases_ai)} AI trigger phrases")

    trigger_words_africa = africa_trigger_words.get()
    logger.info(f"Loaded {len(trigger_words_africa)} Africa trigger words")

    trigger_phrases_africa = africa_trigger_phrases.get()
    logger.info(f"Loaded {len(trigger_phrases_africa)} Africa trigger phrases")

except Exception as e:
    logger.error(f"Error loading trigger files: {str(e)}")

    trigger_words_ai = []
    trigger_phrases_ai = []
    trigger_words_africa = []
    trigger_phrases_africa = []

    # This is good in debug so we can know that we need to fix something
    if DEBUG_MODE:
        raise e

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    + "AppleWebKit/537.36 (KHTML, like Gecko)"
    + "Chrome/91.0.4472.124 Safari/537.36"
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def serve() -> None:
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    source_pb2_grpc.add_SourceServiceServicer_to_server(SourceService(), server)
    server.add_insecure_port(GRPC_ADDRESS)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    try:
        logger.info("Starting gRPC server...")
        serve()
    except Exception as e:
        logger.error(f"Server crashed: {str(e)}", exc_info=True)


def correct_url(url: str) -> str:
    parts = url.split("//", 2)  # Split into scheme and the rest
    if len(parts) == 3 and parts[1] in parts[2]:  # Detect duplicate domain
        return f"{parts[0]}//{parts[2]}"  # Keep only one domain occurrence
    return url


def scrape_news(url: str):

    # Benchmark get_selector
    start_get_selector = time.time()
    html_content, general_selector = get_selector(
        url,
        NEWS_PROMPTS_PATH,
    )
    end_get_selector = time.time()
    logging.info(
        f"get_selector took {end_get_selector - start_get_selector:.2f} seconds"
    )

    # Benchmark BeautifulSoup parsing
    start_parse = time.time()
    soup = BeautifulSoup(html_content, "html.parser")
    end_parse = time.time()
    logging.info(f"HTML parsing took {end_parse - start_parse:.2f} seconds")

    # Benchmark element selection
    start_select = time.time()
    link = soup.select_one(selector=str(general_selector["link"]))
    title = soup.select_one(selector=str(general_selector["title"]))
    end_select = time.time()
    logging.info(f"Element selection took {end_select - start_select:.2f} seconds")

    page_url = None
    if link:
        page_url = link.get("href")

    if page_url and title:
        # Benchmark URL resolution
        start_resolve = time.time()
        page_url = resolve_relative_url(url, page_url)
        end_resolve = time.time()
        logging.info(f"URL resolution took {end_resolve - start_resolve:.2f} seconds")

        # Benchmark news detail scraping
        start_detail = time.time()
        result = (
            try_until(lambda: scrape_news_detail(general_selector, page_url, title))
            or -1  # -1 just avoid retrying the hall thing again because other
        )
        end_detail = time.time()
        logging.info(
            f"News detail scraping took {end_detail - start_detail:.2f} seconds"
        )

        return result


def scrape_news_detail(
    general_selector: dict,
    page_url: str,
    title: Tag,
):
    html_content, page_selector = get_selector(
        page_url,
        NEWS_DETAIL_PROMPTS_PATH,
    )

    soup = BeautifulSoup(html_content, "html.parser")

    body = soup.select_one(selector=str(page_selector["body"]))
    post_date = soup.select_one(selector=str(page_selector["post_date"]))
    image_url_element = soup.select_one(selector=str(page_selector["image_url"]))
    event_date_element = soup.select_one(selector=str(page_selector["event_date"]))

    author_name_element = soup.select_one(selector=str(page_selector["author"]["name"]))  # type: ignore
    author_link_element = soup.select_one(selector=str(page_selector["author"]["link"]))  # type: ignore
    author_image_url_element = soup.select_one(selector=str(page_selector["author"]["image_url"]))  # type: ignore

    author_name = (
        author_name_element.get_text().strip() if author_name_element else None
    )
    author_link = author_link_element.get("href") if author_link_element else None
    author_image_url = (
        author_image_url_element.get("src") if author_image_url_element else None
    )

    if author_image_url is not None:
        author_image_url = resolve_relative_url(page_url, author_image_url)

    if author_link is not None:
        author_link = resolve_relative_url(page_url, author_link)

    if body and post_date:
        body_text = body.get_text().strip()
        if "cookies" in body_text:
            return None
        image_url = image_url_element.get("src") if image_url_element else None

        if image_url is not None:
            image_url = resolve_relative_url(page_url, image_url)

        event_date = (
            event_date_element.get_text().strip() if event_date_element else None
        )

        page_data: NewsDict = {
            "title": title.get_text().strip(),
            "link": page_url,
            "body": body_text,
            "post_date": post_date.get_text().strip(),
            "image_url": image_url,
            "event_date": event_date,
            "author": (
                None
                if author_name is None
                else {
                    "image_url": author_image_url,
                    "link": author_link,
                    "name": author_name,
                }
            ),
        }

        selector: Selector = {
            "author": page_selector["author"],  # type: ignore
            "body": page_selector["body"],
            "event_date": page_selector["event_date"],
            "image_url": page_selector["image_url"],
            "post_date": page_selector["post_date"],
            "link": general_selector["link"],
            "load_more_button": general_selector["load_more_button"],
            "next_button": general_selector["next_button"],
            "title": general_selector["title"],
        }

        return {
            "selector": selector,
            "data": page_data,
        }


def try_until(
    func: Callable[[], None | object],
    max_retries: int = 3,
    error_message: str = "Failed to get valid HTML content and selectors after maximum retries. Please check the prompt or the code.",
) -> object:
    #! FOR THE LOVE OF GOD STOP USING AI!!!!!!!!!! CODE IT YOURSELF or at least REFACTOR THE GENERATED FREAKING CODE!!!!!!!!!!!
    """Retry a function until it returns a non-None value or max retries is reached.

    Args:
        func: The function to retry, which should return None or an object
        max_retries: Maximum number of retry attempts (default: 3)
        error_message: Error message to raise if all retries fail

    Returns:
        object: The first non-None result from func

    Raises:
        Exception: If max_retries is reached without func returning a non-None value
    """
    for _ in range(max_retries):
        result = func()
        if result:
            return result
    raise Exception(error_message)


def get_selector(
    url: str,
    template_path: str,
) -> tuple[str, dict[str, object | dict]]:
    driver = CustomDriver()

    driver.get(url)

    html_content = driver.get_html()
    driver.quit()

    prompt = Prompt(
        template_path=template_path,
        html_content=html_content,
    )

    result = llm.prompt(prompt)
    print(result)

    selector = result.code

    return html_content, selector


@app.get("/")
def root() -> list[dict]:
    """
    Main endpoint that orchestrates the scraping process across all configured sources.

    Returns:
        list[dict]: A list of dictionaries containing scraped content information
    """
    all_results: list[dict] = []

    for source in []:
        logging.debug(f"Processing source: {source['url']}")

        source_results = handle_source(source)

        all_results.extend(source_results)

    logging.debug(f"Total results found: {len(all_results)}")
    logging.debug(all_results)

    return all_results


def handle_source(source: SourceDict):
    url = source["url"]
    trigger_ai = source["trigger_ai"]
    trigger_africa = source["trigger_africa"]
    driver = CustomDriver()
    driver.get(url)
    sleep(3)
    html_content = driver.get_html()

    prompt = Prompt(
        template_path=NEWS_PROMPTS_PATH,
        html_content=html_content,
    )
    result = llm.prompt(prompt)
    print(type(result.code))

    selector = result.code

    next_button_selector = str(selector["next_button"])
    load_more_selector = str(selector["load_more_button"])

    logging.debug(f"Navigating to URL: {url}")
    html: str = ""

    articles = []
    try:
        max_loads: int = 10

        iterator = (
            InfiniteScrollIterator(
                custom_driver=driver,
                css_selector=str(load_more_selector),
                timeout_s=10,
                limit=max_loads,
            )
            if next_button_selector is None
            else PaginationIterator(
                driver=driver,
                css_selector=str(next_button_selector),
                timeout_s=10,
                limit=5,
            )
        )
        for loaded_content in iterator:
            scraped_articles = get_articles(
                url=url,
                trigger_africa=trigger_africa,
                trigger_ai=trigger_ai,
                selector=selector,
                content=loaded_content,
            )
            articles.extend(scraped_articles)

    except Exception as e:
        print(e)
        driver.quit()

    del driver

    return articles


def get_articles(
    url: str,
    trigger_ai: bool,
    trigger_africa: bool,
    selector: dict,
    content: str,
) -> list[NewsAddRequest]:

    logging.debug("Parsing HTML with BeautifulSoup")
    soup = BeautifulSoup(content, "html.parser")

    logging.debug(f"Selecting elements with selector: {selector['title']}")
    elements = soup.select(selector["title"])

    logging.debug(f"Found {len(elements)} title elements")

    logging.debug(f"Selecting links with selector: {selector['link']}")
    links = soup.select(selector["link"])

    logging.debug(f"Found {len(links)} link elements")

    articles: list[NewsAddRequest] = []

    logging.debug(f"Processing {len(elements)} elements")

    for i, element in enumerate(elements):
        logging.debug(f"Processing element {i+1}/{len(elements)}")

        title = element.get_text().strip()
        link = links[i].get("href")

        if link:
            link = resolve_relative_url(url, link)

        logging.debug(f"Title: {title}")
        logging.debug(f"Link: {link}")

        should_add_africa = False

        if trigger_africa:
            logging.debug(f"Checking for Africa triggers in: {title}")

            should_add_africa = contains_triggers(
                title,
                trigger_words_africa,
                trigger_phrases_africa,
            )

            if "africa" in title.lower():
                logging.debug(f"Found Africa keyword in: {title}")

        should_add_ai = False

        if trigger_ai:
            logging.debug(f"Checking for AI triggers in: {title}")

            should_add_ai = contains_triggers(
                title,
                trigger_words_ai,
                trigger_phrases_ai,
            )

            if should_add_ai:
                logging.debug(f"Found AI trigger in: {title}")

        should_add = should_add_ai == trigger_ai and should_add_africa == trigger_africa

        logging.debug(f"Should add this result: {should_add}")

        if should_add:
            # Skip entries with no link (can't fetch additional data)
            if link is None:
                logging.debug("Skipping - link is None")
                continue

            logging.debug(f"Fetching author information from: {link}")
            link = resolve_relative_url(url, link)
            author_response = requests.get(url=link, headers=HEADERS)
            author_soup = BeautifulSoup(author_response.text, "html.parser")

            author: Author | None = None
            # if author_selector is not None:
            #     logging.debug(
            #         f"Looking for author with selector: {author_selector}"
            #     )
            #     author_name_element = author_soup.select_one(
            #         author_selector["name"]
            #     )
            #     author_link_selector = author_selector["link"]
            #     if author_link_selector:
            #         author_link_element = author_soup.select_one(
            #             author_link_selector
            #         )
            #
            #     author = {
            #         "name": (
            #             author_name_element.get_text()
            #             if author_name_element
            #             else "Unknown"
            #         ),
            #         "link": (
            #             str(author_link_element.get("href"))
            #             if author_link_element
            #             else None
            #         ),
            #     }
            #     logging.debug(f"Found author: {author['name']}")

            logging.debug(f"Adding result: {title}")

    logging.debug(f"Adding {len(articles)} results from {url} to all_results")
    return articles


def resolve_relative_url(
    base_url: str,
    url_fragment: str | list[str],
) -> str:
    if isinstance(url_fragment, list):
        url_fragment = "".join(
            url_fragment
        )  # If the URL fragment is too long it gets divided into a list so we need to join it back together

    if url_fragment and url_fragment.startswith("/"):
        parsed_url = urlparse(base_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        url_fragment = f"{base_url}{url_fragment}"

    return correct_url(url_fragment)
