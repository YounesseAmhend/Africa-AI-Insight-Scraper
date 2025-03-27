import asyncio
import datetime
import logging
import time
from typing import Callable

from bs4 import BeautifulSoup, ParserRejectedMarkup, Tag
from ai.llm import Llm
from ai.prompt import Prompt

from grpc import ServicerContext

from constants import (
    AFRICA_TRIGGER_PHRASES_PATH,
    AFRICA_TRIGGER_WORDS_PATH,
    AI_TRIGGER_PHRASES_PATH,
    AI_TRIGGER_WORDS_PATH,
    NEWS_DETAIL_PROMPTS_PATH,
    NEWS_PROMPTS_PATH,
)
from dtypes.news_dict import NewsDict
from dtypes.selector import Selector
from models.news import NewsAdd
from repositories.author_repository import AuthorRepository
from repositories.news_repository import NewsRepository
from protos.author_pb2 import AuthorRequest
from protos.news_pb2 import NewsAddRequest
from protos.source_pb2 import (
    ScrapeRequest,
    ScrapeResponse,
    SourceRequest,
    SourceResponse,
)

from repositories.source_repository import SourceRepository
from protos.source_pb2_grpc import SourceServiceServicer
from settings import DEBUG_MODE, LAST_FETCH_DATE
from utils.custom_driver import CustomDriver
from utils.custom_soup import CustomSoup
from utils.infinite_scrolling_iterator import InfiniteScrollIterator
from utils.pagination_iterator import PaginationIterator
from utils.trigger_file import TriggerFile
from utils.utils import contains_triggers

llm = Llm()

class Source:
    id: int


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
        page_url = CustomSoup.resolve_relative_url(url, page_url)
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
        author_image_url = CustomSoup.resolve_relative_url(page_url, author_image_url)

    if author_link is not None:
        author_link = CustomSoup.resolve_relative_url(page_url, author_link)

    if body and post_date:
        body_text = body.get_text().strip()
        if "cookies" in body_text:
            return None
        image_url = image_url_element.get("src") if image_url_element else None

        if image_url is not None:
            image_url = CustomSoup.resolve_relative_url(page_url, image_url)

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


trigger_words_ai = []
trigger_phrases_ai = []
trigger_words_africa = []
trigger_phrases_africa = []
try:
    ai_trigger_words = TriggerFile(AI_TRIGGER_WORDS_PATH)
    ai_trigger_phrases = TriggerFile(AI_TRIGGER_PHRASES_PATH)
    africa_trigger_words = TriggerFile(AFRICA_TRIGGER_WORDS_PATH)
    africa_trigger_phrases = TriggerFile(AFRICA_TRIGGER_PHRASES_PATH)

    trigger_words_ai = ai_trigger_words.get()
    logging.info(f"Loaded {len(trigger_words_ai)} AI trigger words")

    trigger_phrases_ai = ai_trigger_phrases.get()
    logging.info(f"Loaded {len(trigger_phrases_ai)} AI trigger phrases")

    trigger_words_africa = africa_trigger_words.get()
    logging.info(f"Loaded {len(trigger_words_africa)} Africa trigger words")

    trigger_phrases_africa = africa_trigger_phrases.get()
    logging.info(f"Loaded {len(trigger_phrases_africa)} Africa trigger phrases")

except Exception as e:
    logging.error(f"Error loading trigger files: {str(e)}")

    # This is good in debug so we can know that we need to fix something
    if DEBUG_MODE:
        raise e


def is_valid_source(
    title: str,
    trigger_africa: bool,
    trigger_ai: bool,
) -> bool:
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

    return should_add


class SourceService(SourceServiceServicer):

    def scrape(
        self,
        request: ScrapeRequest,
        context: ServicerContext,
    ) -> ScrapeResponse:

        author_repository = AuthorRepository()
        source_repository = SourceRepository()
        news_repository = NewsRepository()
        sources = source_repository.get_sources()

        driver = CustomDriver()

        for source in sources:

            url = source.url
            trigger_ai = source.triggerAi
            trigger_africa = source.triggerAfrica
            driver.get(url)

            for i in range(3):
                if i > 0:
                    source = source_repository.get_source(source.id)

                selector: Selector = source.selector  # type: ignore
                author_selector = selector["author"]

                next_button_selector = selector["next_button"]
                load_more_selector = selector["load_more_button"]

                logging.debug(f"Navigating to URL: {url}")

                try:
                    limit: int | None = None

                    timeout_s: float = 10
                    iterator = (
                        InfiniteScrollIterator(
                            custom_driver=driver,
                            css_selector=str(load_more_selector),
                            timeout_s=timeout_s,
                            limit=limit,
                        )
                        if next_button_selector is None
                        else PaginationIterator(
                            driver=driver,
                            css_selector=str(next_button_selector),
                            timeout_s=timeout_s,
                            limit=limit,
                        )
                    )
                    for loaded_content in iterator:
                        current_url = driver.driver.execute_script("return window.location.href;")

                        print(f"Current url: {current_url}")

                        logging.debug("Parsing HTML with BeautifulSoup")
                        soup = BeautifulSoup(loaded_content, "html.parser")

                        logging.debug(
                            f"Selecting elements with selector: {selector['title']}"
                        )
                        elements = soup.select(selector["title"])

                        logging.debug(f"Found {len(elements)} title elements")

                        logging.debug(
                            f"Selecting links with selector: {selector['link']}"
                        )
                        links = soup.select(selector["link"])

                        logging.debug(f"Found {len(links)} link elements")

                        logging.debug(f"Processing {len(elements)} elements")

                        for i, element in enumerate(elements):
                            logging.debug(f"Processing element {i+1}/{len(elements)}")

                            title = element.get_text().strip()

                            should_add = is_valid_source(
                                title,
                                trigger_africa=trigger_africa,
                                trigger_ai=trigger_ai,
                            )

                            logging.debug(f"Title: {title}")
                            logging.debug(f"Should add this result: {should_add}")

                            if should_add:
                                news_url = links[i].get("href")

                                if news_url:
                                    news_url = CustomSoup.resolve_relative_url(url, news_url)

                                # Skip entries with no link (can't fetch additional data)
                                if news_url is None:
                                    logging.debug("Skipping - link is None")
                                    continue

                                logging.debug(
                                    f"Fetching author information from: {news_url}"
                                )

                                news_url = CustomSoup.resolve_relative_url(
                                    url, news_url
                                )

                                driver.get(news_url)
                                news_page = driver.get_html()
                                soup = CustomSoup(news_page)

                                author: AuthorRequest | None = None
                                if author_selector is not None:
                                    logging.debug(
                                        f"Looking for author with selector: {author_selector}"
                                    )
                                    author_name = soup.select_text(
                                        author_selector["name"]
                                    )
                                    author_url = soup.select_url(
                                        base_url=url,
                                        css_selector=author_selector["link"],
                                    )

                                    author = AuthorRequest(
                                        name=author_name,
                                        url=author_url,
                                    )
                                    logging.debug(f"Found author: {author.name}")

                                    author_id = author_repository.get_or_create_author(
                                        author
                                    )

                                body = soup.select_text(selector["body"])
                                post_date = soup.select_text(selector["post_date"])
                                image_url = soup.select_url(
                                    css_selector=selector["image_url"],
                                    base_url=url,
                                )

                                if not (body and post_date):
                                    self.addUpdateSource(
                                        request=SourceRequest(
                                            url=source.url,
                                            containsAfricaContent=(
                                                not source.triggerAfrica
                                            ),
                                            containsAiContent=(not source.triggerAi),
                                        )
                                    )
                                    raise Exception(
                                        "The Body selector and the post selector are outdated valid"
                                    )
                                date_formats = [
                                    "%Y-%m-%dT%H:%M:%S",  # ISO 8601
                                    "%Y-%m-%d %H:%M:%S",  # Common datetime format
                                    "%Y/%m/%d %H:%M:%S",  # Slash separated
                                    "%d/%m/%Y %H:%M:%S",  # European format
                                    "%m/%d/%Y %H:%M:%S",  # US format
                                    "%Y-%m-%d",  # Date only
                                    "%d %b %Y",  # 01 Jan 2023
                                    "%b %d, %Y",  # Jan 01, 2023
                                    "%d %B %Y",  # 01 January 2023
                                    "%B %d, %Y",  # January 01, 2023
                                ]
                                date_prefixes = [
                                    "Posted on",
                                    "Posted",
                                    "Published on",
                                    "Published",
                                    "Last updated on",
                                    "Last updated",
                                    "Updated on",
                                    "Updated",
                                    "Created on",
                                    "Created",
                                    "Date:",
                                    "Time:",
                                    ":",
                                ]
                                for prefix in date_prefixes:
                                    post_date = post_date.replace(prefix, "").strip()

                                date = None
                                for fmt in date_formats:
                                    try:
                                        date = datetime.datetime.strptime(
                                            post_date, fmt
                                        )
                                        break
                                    except ValueError:
                                        continue

                                if date is None:
                                    raise ValueError(
                                        f"Could not parse date: {post_date}"
                                    )
                                if (
                                    source.updatedAt
                                    and datetime.datetime.fromisoformat(
                                        source.updatedAt
                                    )
                                    > date
                                ):
                                    logging.debug(
                                        f"Skipping article from {date} as it's older than source's last update {source.updatedAt}"
                                    )
                                    break

                                if LAST_FETCH_DATE > date.date():
                                    logging.debug(
                                        f"Skipping article from {date.date()} as it's older than LAST_FETCH_DATE {LAST_FETCH_DATE}"
                                    )
                                    break
                                author_id = author_id if author_id else None

                                news = NewsAdd(
                                    authorId=author_id,
                                    title=title,
                                    url=url,
                                    sourceId=source.id,
                                    body=body,
                                    postDate=post_date,
                                    imageUrl=image_url,
                                )
                                try:
                                    news_repository.add_news(news)
                                except Exception as e:
                                    print(e)
                                    continue

                                logging.debug(f"Adding result: {title}")
                                
                        driver.get(current_url)

                    source_repository.update_at(
                        source.id,
                        datetime.datetime.now(),
                    )

                    break

                except ParserRejectedMarkup as e:
                    logging.error(
                        f"HTML parsing error scraping source {source.url}: {str(e)}",
                        exc_info=True,
                    )
                    continue
                except KeyError as e:
                    logging.error(
                        f"Missing selector key error scraping source {source.url}: {str(e)}",
                        exc_info=True,
                    )
                    continue
                except AttributeError as e:
                    logging.error(
                        f"Attribute access error scraping source {source.url}: {str(e)}",
                        exc_info=True,
                    )
                    continue
                except ValueError as e:
                    logging.error(
                        f"Value error scraping source {source.url}: {str(e)}",
                        exc_info=True,
                    )
                    continue
                except Exception as e:
                    logging.error(
                        f"Unexpected error scraping source {source.url}: {str(e)}",
                        exc_info=True,
                    )
                    continue

        return ScrapeResponse()

    def addSource(
        self,
        request: SourceRequest,
        context: ServicerContext,
    ) -> SourceResponse:

        result = self.addUpdateSource(request)

        return SourceResponse(
            message=str(
                result
            ),  # * Just for testing purposes otherwise this is completely stupid
        )

    def addUpdateSource(
        self,
        request: SourceRequest,
    ):
        url = request.url

        start_time = time.time()

        result = try_until(
            lambda: scrape_news(url),
            max_retries=3,
        )

        end_time = time.time()
        elapsed_time = end_time - start_time

        logging.info(f"Scraping completed in {elapsed_time:.2f} seconds")

        selector = result["selector"]  # type: ignore

        if selector:
            source_repo = SourceRepository()

            try:
                # Store source with selector
                record_id = source_repo.upsert_source(
                    selector=selector,
                    source=request,
                )

                result["db_record_id"] = record_id  # type: ignore

            except Exception as e:
                logging.error(f"Failed to store source: {e}")

        return result
