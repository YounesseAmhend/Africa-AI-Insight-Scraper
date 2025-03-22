import logging
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, status

from constants import *
from constants import SOURCES
from utils.contains_triggers import contains_triggers
from dtypes.author import Author
from settings import *
from utils.custom_driver import CustomDriver
from utils.trigger_file import TriggerFile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# App configuration
app = FastAPI(
    title="Africa-AI-Insight-Scraper",
    description="Web scraper for AI and Africa-related content",
    version="1.0.0",
)


# Load trigger files
try:
    ai_trigger_words = TriggerFile(AI_TRIGGER_WORDS_PATH)
    ai_trigger_phrases = TriggerFile(AI_TRIGGER_PHRASES_PATH)
    africa_trigger_words = TriggerFile(AFRICA_TRIGGER_WORDS_PATH)
    africa_trigger_phrases = TriggerFile(AFRICA_TRIGGER_PHRASES_PATH)

    trigger_words_ai = ai_trigger_words.get()
    trigger_phrases_ai = ai_trigger_phrases.get()
    trigger_words_africa = africa_trigger_words.get()
    trigger_phrases_africa = africa_trigger_phrases.get()

    logger.info(f"Loaded {len(trigger_words_ai)} AI trigger words")
    logger.info(f"Loaded {len(trigger_phrases_ai)} AI trigger phrases")
    logger.info(f"Loaded {len(trigger_words_africa)} Africa trigger words")
    logger.info(f"Loaded {len(trigger_phrases_africa)} Africa trigger phrases")

except Exception as e:
    logger.error(f"Error loading trigger files: {str(e)}")
    trigger_words_ai = []
    trigger_phrases_ai = []
    trigger_words_africa = []
    trigger_phrases_africa = []
    # The app should break because otherwise we will get a lot of problems
    if DEBUG_MODE:
        raise e

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


@app.get("/")
def root():

    all_results: list[dict] = []
    for source in SOURCES:
        logging.debug(f"Processing source: {source['url']}")

        url = source["url"]
        trigger_ai = source["trigger_ai"]
        trigger_africa = source["trigger_africa"]
        selector = source["selectors"]

        author_selector = selector["author"]
        next_button_selector = selector["next_button"]
        load_more_selector = selector["load_more_button"]

        logging.debug(f"Navigating to URL: {url}")
        html: str = ""
        driver = CustomDriver()
        try:
            driver.get(url)

            if next_button_selector is None:
                logging.debug(
                    f"No pagination found. Using scroll to end with load_more_selector: {load_more_selector}"
                )
                driver.handle_infinite_scroll(load_more_selector, timeout_s=10)
                html = driver.get_html()
            else:
                logging.debug(
                    f"Pagination found. Using next button selector: {next_button_selector}"
                )
                html = driver.handle_pagination(
                    next_button_selector, timeout_s=10, max_pages=5
                )
        except Exception as e:
            print(e)
            driver.quit()
        del driver

        logging.debug("Parsing HTML with BeautifulSoup")
        soup = BeautifulSoup(html, "html.parser")

        logging.debug(f"Selecting elements with selector: {selector['title']}")
        elements = soup.select(selector["title"])
        logging.debug(f"Found {len(elements)} title elements")

        logging.debug(f"Selecting links with selector: {selector['link']}")
        links = soup.select(selector["link"])
        logging.debug(f"Found {len(links)} link elements")

        # assert(len(links) == len(elements))

        source_results = []  # Create a list for results from this source
        logging.debug(f"Processing {len(elements)} elements")

        for i, element in enumerate(elements):
            logging.debug(f"Processing element {i+1}/{len(elements)}")

            title = element.get_text().strip()
            link = links[i].get("href")
            if isinstance(link, list):
                link = "".join(
                    link
                )  # If the link is too long it get divided into a list so we need to get back together

            # Check if link is relative (starts with /) and make it absolute
            if link and link.startswith("/"):
                # Extract domain from the source URL
                parsed_url = urlparse(url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                link = f"{base_url}{link}"

            logging.debug(f"Title: {title}")
            logging.debug(f"Link: {link}")

            # Check for trigger words or phrases
            should_add_africa = False

            # Check for Africa triggers if needed
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

            # Check for AI triggers if needed
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

            # Determine if we should add this result based on trigger requirements
            should_add = (
                should_add_ai == trigger_ai and should_add_africa == trigger_africa
            )
            logging.debug(f"Should add this result: {should_add}")

            # Add the result if it matches any trigger
            if should_add:
                if link is None:
                    logging.debug("Skipping - link is None")
                    continue

                logging.debug(f"Fetching author information from: {link}")
                author_response = requests.get(url=link, headers=HEADERS)
                author_soup = BeautifulSoup(author_response.text, "html.parser")

                author: Author | None = None

                if author_selector is not None:
                    logging.debug(
                        f"Looking for author with selector: {author_selector}"
                    )
                    author_name_element = author_soup.select_one(
                        author_selector["name"]
                    )
                    author_link_selector = author_selector["link"]
                    if author_link_selector:
                        author_link_element = author_soup.select_one(
                            author_link_selector
                        )

                    author = {
                        "name": (
                            author_name_element.get_text()
                            if author_name_element
                            else "Unknown"
                        ),
                        "link": (
                            str(author_link_element.get("href"))
                            if author_link_element
                            else None
                        ),
                    }
                    logging.debug(f"Found author: {author['name']}")

                logging.debug(f"Adding result: {title}")
                source_results.append(
                    {
                        "title": title,
                        "link": link,
                        "author": author,
                    }
                )

        # Add results from this source to the overall results
        logging.debug(f"Adding {len(source_results)} results from {url} to all_results")
        all_results.extend(source_results)

    logging.debug(f"Total results found: {len(all_results)}")
    logging.debug(all_results)
    return all_results
