import logging
from typing import Callable
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, Tag
from fastapi import FastAPI

from ai.llm import Llm, Prompt
from constants import *
from constants import SOURCES
from utils.infinite_scrolling_iterator import InfiniteScrollIterator
from utils.pagination_iterator import PaginationIterator
from utils.utils import contains_triggers
from dtypes.author import Author
from settings import *
from utils.custom_driver import CustomDriver
from utils.trigger_file import TriggerFile
from time import sleep

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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


@app.get("/add")
def add_source():

    source = {
        "url": "https://www.up.ac.za/news",
        "trigger_africa": False,
        "trigger_ai": True,
    }

    max_retries: int = 3

    url = source["url"]
    
    return try_until(
        lambda: scrape_news(url),
        max_retries=max_retries,
    )


def scrape_news(url: str):
    html_content, selector = get_selector(
        url,
        NEWS_PROMPTS_PATH,
    )

    soup = BeautifulSoup(html_content, "html.parser")

    link = soup.select_one(selector=str(selector["link"]))
    title = soup.select_one(selector=str(selector["title"]))        

    page_url= None
    if link:
        page_url = link.get("href")
        page_url = href_link(url, page_url)

    if page_url and title:
        return (
            try_until(lambda: scrape_news_detail(page_url, title)) ## here extract the selectors and
            or -1  # -1 just avoid retrying the hall thing again because other
        )


def scrape_news_detail(
    url: str,
    title: Tag,
):
    html_content, selector = get_selector(
        url,
        NEWS_DETAIL_PROMPTS_PATH,
    )

    soup = BeautifulSoup(html_content, "html.parser")

    body = soup.select_one(selector=str(selector["body"]))
    post_date = soup.select_one(selector=str(selector["post_date"]))

    if body and post_date:
        body_text = body.get_text().strip()
        if "cookies" in body_text:
            return None
        return {
            "title": title.get_text().strip(),
            "body": body_text,
            "post_date": post_date.get_text().strip(),
        }


def try_until(
    func: Callable[[], None | object],
    max_retries: int = 3,
    message: str = "Failed to get valid HTML content and selectors after maximum retries. Please check the prompt or the code.",
) -> object:
    """Retry a function until it returns a non-None value or max retries is reached.

    Args:
        func: The function to retry, which should return None or an object
        max_retries: Maximum number of retry attempts (default: 3)
        message: Error message to raise if all retries fail (default: generic message)

    Returns:
        object: The first non-None result from func

    Raises:
        Exception: If max_retries is reached without func returning a non-None value
    """
    for _ in range(max_retries):
        result = func()
        if result:
            return result
    raise Exception(message)


def get_selector(
    url: str,
    template_path: str,
) -> tuple[str, dict]:
    driver = CustomDriver()

    driver.get(url)
    sleep(3)  # Wait for JS to load

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

    for source in SOURCES:
        logging.debug(f"Processing source: {source['url']}")

        source_results = handle_source(source)

        all_results.extend(source_results)

    logging.debug(f"Total results found: {len(all_results)}")
    logging.debug(all_results)

    return all_results


def handle_source(source: Source):
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
        max_loads = 10

        if next_button_selector is None:
            logging.debug(
                f"No pagination found. Using scroll to end with load_more_selector: {load_more_selector}"
            )
            for page in InfiniteScrollIterator(
                custom_driver=driver,
                css_selector=str(load_more_selector),
                timeout_s=10,
                max_loads=max_loads,
            ):
                new_articles = get_articles(
                    url=url,
                    trigger_africa=trigger_africa,
                    trigger_ai=trigger_ai,
                    selector=selector,
                    content=page,
                )
                articles.extend(new_articles)
        else:
            logging.debug(
                f"Pagination found. Using next button selector: {next_button_selector}"
            )
            html = driver.handle_pagination(
                str(next_button_selector),
                timeout_s=10,
                max_pages=5,
            )

    except Exception as e:
        print(e)
        driver.quit()

    del driver

    articles = get_articles(
        url,
        trigger_ai,
        trigger_africa,
        selector,
        html,
    )
    return articles


def get_articles(
    url: str,
    trigger_ai: bool,
    trigger_africa: bool,
    selector: dict,
    content: str,
) -> list[dict]:
    logging.debug("Parsing HTML with BeautifulSoup")
    soup = BeautifulSoup(content, "html.parser")

    logging.debug(f"Selecting elements with selector: {selector['title']}")
    elements = soup.select(selector["title"])

    logging.debug(f"Found {len(elements)} title elements")

    logging.debug(f"Selecting links with selector: {selector['link']}")
    links = soup.select(selector["link"])

    logging.debug(f"Found {len(links)} link elements")

    articles = []

    logging.debug(f"Processing {len(elements)} elements")

    for i, element in enumerate(elements):
        logging.debug(f"Processing element {i+1}/{len(elements)}")

        title = element.get_text().strip()
        link = links[i].get("href")

        link = href_link(url, link)

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

            articles.append(
                {
                    "title": title,
                    "link": link,
                    "author": author,
                }
            )

    logging.debug(f"Adding {len(articles)} results from {url} to all_results")
    return articles

def href_link(url, link):
    if isinstance(link, list):
        link = "".join(
                link
            )  # If the link is too long it get divided into a list so we need to get back together

    if link and link.startswith("/"):
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        link = f"{base_url}{link}"
    return link
