import datetime
import logging
import time

import pytz
from bs4 import BeautifulSoup, ParserRejectedMarkup, Tag
from grpc import ServicerContext

from ai.llm import Llm
from ai.prompt import Prompt
from constants import (AFRICA_TRIGGER_PHRASES_PATH, AFRICA_TRIGGER_WORDS_PATH,
                       AI_TRIGGER_PHRASES_PATH, AI_TRIGGER_WORDS_PATH)
from dtypes.author_dict import AuthorDict
from dtypes.selector import Selector
from iterators.infinite_scrolling_iterator import InfiniteScrollIterator
from iterators.pagination_iterator import PaginationIterator
from models.author import Author
from models.news import NewsAdd
from models.source import Source, SourceUpdate
from protos.source_pb2 import (ScrapeRequest, ScrapeResponse, SourceRequest,
                               SourceResponse)
from protos.source_pb2_grpc import SourceServiceServicer
from repositories.author_repository import AuthorRepository
from repositories.source_repository import SourceRepository
from services.news_service import NewsService
from settings import DEBUG_MODE, LAST_FETCH_DATE
from utils.checker import Checker
from utils.custom_driver import CustomDriver
from utils.custom_soup import CustomSoup
from utils.helper import Helpers

from utils.trigger_utils import TriggerFile, TriggerUtils

from ..utils.scrape_utils import ScrapeUtils

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
)
utc = pytz.UTC
llm = Llm()


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

    # This is good in info so we can know that we need to fix something
    if DEBUG_MODE:
        raise e


def is_valid_article(
    title: str,
    trigger_africa: bool,
    trigger_ai: bool,
) -> bool:
    should_add_africa = False

    if trigger_africa:
        logging.info(f"Checking for Africa triggers in: {title}")

        should_add_africa = TriggerUtils.contains_triggers(
            title,
            trigger_words_africa,
            trigger_phrases_africa,
        )

        if "africa" in title.lower():
            logging.info(f"Found Africa keyword in: {title}")

    should_add_ai = False

    if trigger_ai:
        logging.info(f"Checking for AI triggers in: {title}")

        should_add_ai = TriggerUtils.contains_triggers(
            title,
            trigger_words_ai,
            trigger_phrases_ai,
        )

        if should_add_ai:
            logging.info(f"Found AI trigger in: {title}")

    should_add = should_add_ai == trigger_ai and should_add_africa == trigger_africa

    return should_add


class SourceService(SourceServiceServicer):
    def scrape(
        self,
        request: ScrapeRequest,
        context: ServicerContext,
    ) -> ScrapeResponse:
        self._scrape()
        return ScrapeResponse()

    def _scrape(self):
        author_repository = AuthorRepository()
        source_repository = SourceRepository()
        news_repository = NewsService()

        sources = source_repository.get_sources()

        driver = CustomDriver()

        for source in sources:
            self._handle_source(
                author_repository,
                source_repository,
                news_repository,
                driver,
                source,
            )

        driver.quit()

    def _handle_source(
        self,
        author_repository: AuthorRepository,
        source_repository: SourceRepository,
        news_repository: NewsService,
        driver: CustomDriver,
        source: Source,
    ):
        url = source.url
        trigger_ai = source.triggerAi
        trigger_africa = source.triggerAfrica
        driver.get(url)

        MAX_RETRIES = 3

        for i in range(MAX_RETRIES):
            if i > 0:
                source = source_repository.get_source(source.id)

            selector: Selector = source.selector  # type: ignore
            author_selector = selector["author"]

            next_button_selector = selector["next_button"]
            load_more_selector = selector["load_more_button"]

            logging.info(f"Navigating to URL: {url}")

            try:
                limit: int | None = None

                timeout_s: float = 10
                self._handle_content(
                    author_repository,
                    source_repository,
                    news_repository,
                    driver,
                    source,
                    url,
                    trigger_ai,
                    trigger_africa,
                    selector,
                    author_selector,
                    next_button_selector,
                    load_more_selector,
                    limit,
                    timeout_s,
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

    def _handle_content(
        self,
        author_repository: AuthorRepository,
        source_repository: SourceRepository,
        news_repository: NewsService,
        driver: CustomDriver,
        source: Source,
        url: str,
        trigger_ai: bool,
        trigger_africa: bool,
        selector: Selector,
        author_selector: AuthorDict | None,
        next_button_selector: str | None,
        load_more_selector: str | None,
        limit: int | None,
        timeout_s: float,
    ) -> None:
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
            try:
                self._handle_articles(
                    author_repository,
                    news_repository,
                    driver,
                    source,
                    url,
                    trigger_ai,
                    trigger_africa,
                    selector,
                    author_selector,
                    loaded_content,
                )
            except StopIteration:
                break
            driver.get(current_url)

        source_repository.update_at(
            source.id,
            datetime.datetime.now(),
        )

    def _handle_articles(
        self,
        author_repository: AuthorRepository,
        news_repository: NewsService,
        driver: CustomDriver,
        source: Source,
        url: str,
        trigger_ai: bool,
        trigger_africa: bool,
        selector: Selector,
        author_selector: AuthorDict | None,
        loaded_content: str,
    ):
        logging.info("Parsing HTML with BeautifulSoup")
        soup = BeautifulSoup(loaded_content, "html.parser")

        logging.info(f"Selecting elements with selector: {selector['title']}")
        elements = soup.select(selector["title"])

        logging.info(f"Found {len(elements)} title elements")

        logging.info(f"Selecting links with selector: {selector['link']}")
        links = soup.select(selector["link"])

        logging.info(f"Found {len(links)} link elements")

        logging.info(f"Processing {len(elements)} elements")

        for i, element in enumerate(elements):
            logging.info(f"Processing element {i + 1}/{len(elements)}")

            title = element.get_text().strip()

            should_add = is_valid_article(
                title,
                trigger_africa=trigger_africa,
                trigger_ai=trigger_ai,
            )

            logging.info(f"Title: {title}")
            logging.info(f"Should add this result: {should_add}")

            if should_add:
                news_url = links[i].get("href")

                if news_url:
                    news_url = CustomSoup.resolve_relative_url(url, news_url)

                    # Skip entries with no link (can't fetch additional data)
                if news_url is None:
                    logging.info("Skipping - link is None")
                    continue

                logging.info(f"Fetching author information from: {news_url}")

                news_url = CustomSoup.resolve_relative_url(url, news_url)

                driver.get(news_url)
                news_page = driver.get_html()
                soup = CustomSoup(news_page)

                author_id = self._get_create_author(
                    author_repository,
                    url,
                    trigger_ai,
                    trigger_africa,
                    author_selector,
                    soup,
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
                            containsAfricaContent=(not source.triggerAfrica),
                            containsAiContent=(not source.triggerAi),
                        )
                    )
                    raise Exception(
                        "The Body selector and the post selector are outdated valid"
                    )

                date = Checker.get_date(post_date)

                if date is None:
                    raise ValueError(f"Could not parse date: {post_date}")
                if source.updatedAt and datetime.datetime.fromisoformat(
                    source.updatedAt
                ).replace(tzinfo=pytz.UTC) > date.replace(tzinfo=pytz.UTC):
                    logging.info(
                        f"Skipping article from {date} as it's older than source's last update {source.updatedAt}"
                    )
                    raise StopIteration

                if LAST_FETCH_DATE > date.date():
                    logging.info(
                        f"Skipping article from {date.date()} as it's older than LAST_FETCH_DATE {LAST_FETCH_DATE}"
                    )
                    raise StopIteration
                author_id = author_id if author_id else None

                try:
                    logging.info(
                        f"Creating NewsAdd object with: authorId={author_id}, title={title}, url={url}, sourceId={source.id}"
                    )
                    logging.info(
                        f"Body length: {len(body)}, Post date: {post_date}, Image URL: {image_url}"
                    )
                    news = NewsAdd(
                        authorId=author_id,
                        title=title,
                        url=news_url,
                        sourceId=source.id,
                        body=body,
                        postDate=post_date,
                        imageUrl=image_url,
                    )
                    logging.info("Successfully created NewsAdd object")
                except Exception:
                    self.addUpdateSource(
                        request=SourceRequest(
                            url=source.url,
                            containsAfricaContent=(not source.triggerAfrica),
                            containsAiContent=(not source.triggerAi),
                        )
                    )
                    raise Exception("The detail selector are invalid")

                try:
                    news_repository.add_news(news)
                except Exception as e:
                    print(e)
                    continue

                logging.info(f"Adding result: {title}")

    def _get_create_author(
        self,
        author_repository: AuthorRepository,
        url: str,
        trigger_ai: bool,
        trigger_africa: bool,
        author_selector: AuthorDict | None,
        soup: CustomSoup,
    ) -> int:
        author: Author | None = None
        if author_selector is not None:
            logging.info(f"Looking for author with selector: {author_selector}")
            author_name = soup.select_text(author_selector["name"])
            author_url = soup.select_url(
                base_url=url,
                css_selector=author_selector["link"],
            )

            image_url = soup.select_url(
                base_url=url,
                css_selector=author_selector["image_url"],
            )

            try:
                if Checker.is_date(author_name) or (
                    author_name and not author_name.strip()
                ):
                    raise ValueError(f"Invalid author name: {author_name}")
                if author_url and not Checker.is_valid_url(author_url):
                    raise ValueError(f"Invalid author URL: {author_url}")
                if image_url and not Checker.is_valid_url(image_url):
                    raise ValueError(f"Invalid image URL: {image_url}")

                author = Author(
                    name=author_name,
                    url=author_url,
                    image_url=image_url,
                )

                logging.info(f"Found author: {author.name}")

                author_id = author_repository.get_or_create_author(author)
            except Exception:
                self.addUpdateSource(
                    SourceUpdate(
                        url=url,
                        containsAfricaContent=(not trigger_africa),
                        containsAiContent=(not trigger_ai),
                    )
                )
                raise Exception(
                    "The Body selector and the post selector are outdated valid"
                )
        else:
            author_id = author_repository.get_or_create_author(
                Author(name=None, url=None, image_url=None)
            )

        return author_id

    def addSource(
        self,
        request: SourceRequest,
        context: ServicerContext,
    ) -> SourceResponse:
        start_time = time.time()
        result = self.addUpdateSource(request)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"addSource completed in {elapsed_time:.2f} seconds")

        return SourceResponse(
            message=str(
                result
            ),  # * Just for testing purposes otherwise this is completely stupid
        )

    def addUpdateSource(
        self,
        request: SourceRequest | SourceUpdate,
    ):
        url = request.url

        start_time = time.time()

        result = Helpers.try_until(
            lambda: ScrapeUtils.scrape_news(url),
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
