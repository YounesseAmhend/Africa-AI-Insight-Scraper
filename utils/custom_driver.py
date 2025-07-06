import os
import sys
import tempfile
from lib2to3.pgen2 import driver
from time import sleep

import requests
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from iterators.infinite_scrolling_iterator import InfiniteScrollIterator
from iterators.pagination_iterator import PaginationIterator
from settings import DEBUG_MODE
from utils.logger import logger


class CustomDriver:
    DEFAULT_TIMEOUT_S = 10
    DRIVER_TIMEOUT_S = 300  # Increased timeout for driver operations

    def __init__(self) -> None:
        # Use the correct path for Edge driver in Docker
        EDGE_DRIVER_PATH = "/opt/msedgedriver/msedgedriver"
        self.service = Service(EDGE_DRIVER_PATH)
        self.options = webdriver.EdgeOptions()

        if not DEBUG_MODE:
            self.options.add_argument("--headless")

        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")

        # Set page load timeout and script timeout
        self.driver = webdriver.Edge(service=self.service, options=self.options)
        self.driver.set_page_load_timeout(self.DRIVER_TIMEOUT_S)
        self.driver.set_script_timeout(self.DRIVER_TIMEOUT_S)

        # Further anti-detection: modify navigator.webdriver property using CDP
        # This helps bypass more sophisticated detection mechanisms
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
            },
        )

        # Initialize WebDriverWait for waiting operations with default timeout
        self.wait = WebDriverWait(self.driver, timeout=__class__.DEFAULT_TIMEOUT_S)

        # Initialize ActionChains for complex mouse and keyboard interactions
        self.actions = ActionChains(self.driver)

    def get(self, url: str) -> None:
        self.driver.get(url)

    def handle_infinite_scroll(
        self,
        css_selector: str | None,
        timeout_s: float = DEFAULT_TIMEOUT_S,
        max_loads: int = 20,
    ) -> str:
        logger.debug("Handling infinite scrolling...")
        html = ""
        for page in InfiniteScrollIterator(self, css_selector, timeout_s, max_loads):
            html += page
        return html

    def handle_pagination(
        self,
        css_selector: str,
        timeout_s: float = DEFAULT_TIMEOUT_S,
        max_pages: int = 20,
    ) -> str:
        logger.debug("Handling pagination...")
        html: str = ""
        for page in PaginationIterator(self, css_selector, timeout_s, limit=max_pages):
            html += page
        return html

    def nextPage(
        self,
        css_selector: str,
        timeout_s: float = DEFAULT_TIMEOUT_S,
    ) -> None:
        wait = self.wait
        if timeout_s != self.DEFAULT_TIMEOUT_S:
            wait = WebDriverWait(self.driver, timeout=timeout_s)

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            sleep(0.5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        sleep(1)

        try:
            next_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView(true);", next_button
            )
            sleep(0.5)

            try:
                self.driver.execute_script("arguments[0].click();", next_button)
            except Exception:
                self.actions.move_to_element(next_button).click().perform()

            sleep(2)

        except Exception as e:
            logger.error(f"Error type: {type(e).__name__}")
            if isinstance(e, TimeoutException):
                logger.error("Timeout waiting for next button to be clickable")
            elif isinstance(e, ElementNotInteractableException):
                logger.error("Next button found but not clickable")
            elif isinstance(e, NoSuchElementException):
                logger.error("Next button element not found in the DOM")
            elif isinstance(e, StaleElementReferenceException):
                logger.error("Next button reference is stale (page may have changed)")
            elif isinstance(e, ElementClickInterceptedException):
                logger.error("Click was intercepted by another element")

            # Signal the end of pagination by raising StopIteration
            # This will be caught by the PaginationIterator
            raise StopIteration

    def get_html(self) -> str:
        try:
            logger.info("Waiting for the Page fully loaded, retrieving HTML source")

            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState")
                == "complete",
            )
            logger.info("Page fully loaded, retrieving HTML source")
            return self.driver.page_source
        except Exception as e:
            logger.error(f"Error while getting page HTML: {str(e)}")
            logger.warning("Returning current page source despite error")
            return self.driver.page_source

    def download_file(self, link: str) -> str:

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            # Download the file from the link
            response = requests.get(link)
            response.raise_for_status()

            # Write the content to the temporary file
            tmp_file.write(response.content)
            tmp_file_path = tmp_file.name

        # Read the content from the temporary file
        with open(tmp_file_path, "r") as file:
            content = file.read()

        return content

    def __del__(self):
        try:
            self.driver.quit()
            # Cleanup the temporary user data directory

        except Exception as e:
            print(f"Error during driver cleanup: {str(e)}", file=sys.stderr)

    def quit(self):
        self.driver.quit()
        # Also clean up the user data directory when explicitly quitting
