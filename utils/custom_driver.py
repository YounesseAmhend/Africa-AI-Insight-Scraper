import logging
import os
from time import sleep

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

from settings import DEBUG_MODE
from utils.infinite_scrolling_iterator import InfiniteScrollIterator
from utils.pagination_iterator import PaginationIterator


class CustomDriver:

    DEFAULT_TIMEOUT_S = 2.5

    def __init__(self) -> None:
        EDGE_DRIVER_PATH = (
            "bin/msedgedriver.exe" if os.name == "nt" else "bin/msedgedriver"
        )  # check if windows
        self.service = Service(EDGE_DRIVER_PATH)
        self.options = webdriver.EdgeOptions()

        if not DEBUG_MODE:
            self.options.add_argument("--headless")

        # Disable automation detection
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)

        # Performance optimization arguments
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-browser-side-navigation")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-features=NetworkService")
        self.options.add_argument("--disable-features=VizDisplayCompositor")
        self.options.add_argument("--disable-software-rasterizer")
        self.options.add_argument("--ignore-certificate-errors")

        self.driver = webdriver.Edge(service=self.service, options=self.options)
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

        self.wait = WebDriverWait(self.driver, timeout=__class__.DEFAULT_TIMEOUT_S)
        self.actions = ActionChains(self.driver)

    def get(self, url: str) -> None:
        self.driver.get(
            url,
        )

    def handle_infinite_scroll(
        self,
        css_selector: str | None,
        timeout_s: float = DEFAULT_TIMEOUT_S,
        max_loads: int = 20,
    ) -> str:
        logging.debug("Handling infinite scrolling...")

        
        # Create and return the iterator
        html = ""
        for page in InfiniteScrollIterator(
            self,
            css_selector,
            timeout_s,
            max_loads,
        ):
            html += page

        return html

    def handle_pagination(
        self,
        css_selector: str,
        timeout_s: float = DEFAULT_TIMEOUT_S,
        max_pages: int = 20,
    ) -> str:
        logging.debug("Handling pagination...")

        html: str = ""

        for page in PaginationIterator(
            self,
            css_selector,
            timeout_s,
            limit=max_pages,
        ):
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
            # Scroll down to bottom
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            # Wait to load page
            sleep(0.5)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        sleep(1)  # Smooth scrolling

        try:
            # Wait for the "Next" button to appear
            next_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )

            # Scroll the button into view
            self.driver.execute_script(
                "arguments[0].scrollIntoView(true);", next_button
            )

            # Add a small delay to ensure the page is settled
            sleep(0.5)

            # Try JavaScript click first to avoid intercepted clicks
            try:
                self.driver.execute_script("arguments[0].click();", next_button)
            except Exception:
                # If JavaScript click fails, try moving to the element first
                self.actions.move_to_element(next_button).click().perform()

            # Wait for new content to load
            sleep(2)

        except Exception as e:
            # logging.debug(f"No more 'Next' button found or error: {str(e)}")
            logging.error(f"Error type: {type(e).__name__}")
            if isinstance(e, TimeoutException):
                logging.error("Timeout waiting for next button to be clickable")
            elif isinstance(e, ElementNotInteractableException):
                logging.error("Next button found but not clickable")
            elif isinstance(e, NoSuchElementException):
                logging.error("Next button element not found in the DOM")
            elif isinstance(e, StaleElementReferenceException):
                logging.error("Next button reference is stale (page may have changed)")
            elif isinstance(e, ElementClickInterceptedException):
                logging.error("Click was intercepted by another element")

            raise StopIteration

    def get_html(self) -> str:
        return self.driver.page_source

    def __del__(self):
        """
        Destructor method to ensure the driver is properly closed when the object is garbage collected.
        This helps prevent memory leaks and orphaned browser processes.
        """
        try:
            self.driver.quit()
        except Exception as e:
            # Can't use logging here as it might be unavailable during garbage collection
            import sys

            print(f"Error during driver cleanup: {str(e)}", file=sys.stderr)

    def quit(self):
        self.driver.quit()
