from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from protocols.custom_driver_protocol import CustomDriverProtocol
from utils.logger import logger


class InfiniteScrollIterator:

    def __init__(
        self,
        custom_driver: CustomDriverProtocol,
        css_selector: str | None,
        timeout_s: float,
        limit: int | None = 20,
    ):

        self.wait = WebDriverWait(custom_driver.driver, timeout=timeout_s)
        self.custom_driver = custom_driver
        self.css_selector = css_selector if css_selector and self._selector_exists(css_selector) else None
        self.max_loads = limit
        self.current_load = 0
        self.html: str = ""

    def __iter__(self):
        return self
    
    def _selector_exists(self, css_selector: str) -> bool:
        """Check if a CSS selector exists on the page
        
        :param css_selector: CSS selector to check
        :return: True if selector exists, False otherwise
        """
        try:
            self.custom_driver.driver.find_element(By.CSS_SELECTOR, css_selector)
            return True
        except NoSuchElementException:
            return False

    def __next__(self) -> str:
        if self.max_loads and self.current_load >= self.max_loads:
            raise StopIteration

        if self.current_load == 0:
            self.current_load += 1
            self.html = self.custom_driver.get_html()
            return self.html

        try:
            last_height = self.custom_driver.driver.execute_script(
                "return document.body.scrollHeight"
            )
            # Scroll down to bottom
            self.custom_driver.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            sleep(1)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.custom_driver.driver.execute_script(
                "return document.body.scrollHeight"
            )

            # If height didn't change and no load more button, we're at the end
            if new_height == last_height and self.css_selector is None:
                raise StopIteration

            # If there's a load more button, try to click it
            if self.css_selector:
                try:
                    load_more_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, self.css_selector))
                    )
                    # Scroll to the button and click it
                    self.custom_driver.driver.execute_script(
                        "arguments[0].scrollIntoView(true);", load_more_button
                    )
                    sleep(0.5)
                    load_more_button.click()
                    # Wait for new content to load
                    sleep(2)
                    # Get the updated page content
                    self.current_load += 1
                    new_html: str = self.custom_driver.get_html()[len(self.html) :]
                    self.html += new_html
                    return new_html
                except (TimeoutException, NoSuchElementException):
                    logger.debug("No more 'Load More' button found")
                    raise StopIteration
            else:
                # If we're just scrolling without a button and content loaded
                if new_height > last_height:
                    self.current_load += 1
                    return self.custom_driver.get_html()
                else:
                    raise StopIteration

        except Exception as e:
            logger.error(f"Error during infinite scrolling: {str(e)}")
            raise StopIteration
