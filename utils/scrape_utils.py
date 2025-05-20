import time

from ai.llm import Llm
from constants import NEWS_DETAIL_PROMPTS_PATH, NEWS_PROMPTS_PATH
from dtypes.news_dict import NewsDict
from dtypes.selector import Selector
from models.news import NewsAdd
from utils.checker import Checker
from utils.custom_soup import CustomSoup
from utils.helper import Helpers
from utils.logger import logger
from utils.selector_generator import SelectorGenerator


class ScrapeUtils:
    @staticmethod
    def scrape_news(url: str):
        try:
            # Benchmark get_selector
            start_get_selector = time.time()
            html_content, general_selector = SelectorGenerator.get_scraping_selectors(
                url,
                NEWS_PROMPTS_PATH,
            )
            end_get_selector = time.time()
            logger.info(
                f"get_selector took {end_get_selector - start_get_selector:.2f} seconds"
            )

            # Benchmark BeautifulSoup parsing
            start_parse = time.time()
            soup = CustomSoup(html_content)
            end_parse = time.time()
            logger.info(f"HTML parsing took {end_parse - start_parse:.2f} seconds")

            # Benchmark element selection
            start_select = time.time()
            page_url = soup.select_url(
                base_url=url, css_selector=str(general_selector["link"])
            )
            title = soup.select_text(css_selector=str(general_selector["title"]))
            end_select = time.time()
            logger.info(f"Element selection took {end_select - start_select:.2f} seconds")

            if page_url and title:
                # Benchmark URL resolution
                start_resolve = time.time()
                page_url = CustomSoup.resolve_relative_url(url, page_url)
                end_resolve = time.time()
                logger.info(
                    f"URL resolution took {end_resolve - start_resolve:.2f} seconds"
                )

                # Benchmark news detail scraping
                start_detail = time.time()
                result = (
                    Helpers.try_until(
                        lambda: __class__.scrape_news_detail(
                            general_selector=general_selector,
                            page_url=page_url,
                            base_url=url,
                            title=title,
                        ),
                        error_message="Failed in scrape_news_detail",
                    )
                    or -1  # -1 just avoid retrying the hall thing again because other
                )
                end_detail = time.time()
                logger.info(
                    f"News detail scraping took {end_detail - start_detail:.2f} seconds"
                )

                return result
        except Exception as e:
            logger.error(f"Failed to scrape news: {str(e)}")

    @staticmethod
    def scrape_news_detail(
        general_selector: dict,
        page_url: str,
        base_url: str,
        title: str,
    ):
        logger.info(f"Scraping news details {base_url}")
        html_content, page_selector = SelectorGenerator.get_scraping_selectors(
            page_url,
            NEWS_DETAIL_PROMPTS_PATH,
        )

        soup = CustomSoup(html_content)

        try:
            logger.info("Starting to scrape news details")

            # Logging element selection
            start_time = time.time()
            body: str | None = soup.select_text(str(page_selector["body"]))
            post_date: str | None = soup.select_text(str(page_selector["post_date"]))
            image_url = soup.select_url(
                base_url=base_url, css_selector=str(page_selector["image_url"])
            )
            event_date = soup.select_text(css_selector=str(page_selector["event_date"]))
            end_time = time.time()
            logger.info(f"Element selection took {end_time - start_time:.2f} seconds")

            # Logging author information extraction
            start_time = time.time()
            author_name = soup.select_text(
                str(page_selector["author"]["name"])
                if isinstance(page_selector["author"], dict)
                else None
            )
            author_link = soup.select_url(
                base_url=base_url,
                css_selector=(
                    str(page_selector["author"]["link"])
                    if isinstance(page_selector["author"], dict)
                    else None
                ),
            )
            author_image_url = soup.select_url(
                base_url=base_url,
                css_selector=(
                    str(page_selector["author"]["image_url"])
                    if isinstance(page_selector["author"], dict)
                    else None
                ),
            )
            end_time = time.time()
            logger.info(
                f"Author element selection took {end_time - start_time:.2f} seconds"
            )

            if author_image_url is not None:
                logger.info(f"Resolving author image URL: {author_image_url}")
                author_image_url = CustomSoup.resolve_relative_url(
                    page_url, author_image_url
                )

            if author_link is not None:
                logger.info(f"Resolving author link: {author_link}")
                author_link = CustomSoup.resolve_relative_url(page_url, author_link)

            if body:
                logger.info(f"Body text length: {len(body)} characters")

                if "cookies" in body:
                    logger.warning("Found 'cookies' in body text, skipping article")
                    return None

                if image_url is not None:
                    logger.info(f"Resolving main image URL: {image_url}")
                    image_url = CustomSoup.resolve_relative_url(page_url, image_url)

                page_data: NewsDict = {
                    "title": title,
                    "link": page_url,
                    "body": body,
                    "post_date": post_date,
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

                logger.info("Validating news data structure")
                try:
                    NewsAdd(
                        authorId=None,
                        title=title,
                        url=page_url,
                        sourceId=0,
                        body=body,
                        postDate=post_date,
                        imageUrl=image_url,
                        categoryId=None,  # will add it later in the news service
                    )
                except ValueError as e:
                    logger.info(f"Validation error: {e}")
                    logger.error(f"Validation error: {e}")
                    return None

                # Logging selector validation
                if image_url and not Checker.is_valid_url(image_url):
                    logger.warning(f"Invalid image URL: {image_url}")
                    page_selector["image_url"] = None

                if author_name and not author_name.strip():
                    logger.warning("Empty author name found")
                    page_selector["author"] = None

                if author_name and Checker.is_date(author_name):
                    logger.warning(f"Author name appears to be a date: {author_name}")
                    page_selector["author"] = None

                if author_image_url and not Checker.is_valid_url(author_image_url):
                    logger.warning(f"Invalid author image URL: {author_image_url}")
                    page_selector["author"]["image_url"] = None  # type: ignore

                if author_link and not Checker.is_valid_url(author_link):
                    logger.warning(f"Invalid author link: {author_link}")
                    page_selector["author"]["link"] = None  # type: ignore

                if image_url and not Checker.is_valid_url(image_url):
                    error_msg = f"Invalid author image URL: {image_url}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)

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

                logger.info("Successfully scraped news details")
                return {
                    "selector": selector,
                    "data": page_data,
                }
            else:
                raise Exception(f"Body or postdate does not exists {body} {post_date}")
        except Exception as e:
            logger.info(f"Failed to scrape news details: {str(e)}")
            logger.error(f"Failed to scrape news details: {str(e)}")
