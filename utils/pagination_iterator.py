import logging
from typing import Protocol

from selenium.webdriver.edge.webdriver import WebDriver
from settings import DEBUG_MODE


class CustomDriverProtocol(Protocol):
    driver: WebDriver
    def get_html(self) -> str: ...
    def nextPage(
        self,
        
        css_selector: str,
        timeout_s: float,
    ) -> None: ...


class PaginationIterator:
    def __init__(
        self,
        driver: CustomDriverProtocol,
        css_selector: str,
        timeout_s: float,
        limit: int = 20,
    ) -> None:
        self.currentPage = 1
        self.limit = limit
        self.driver = driver
        self.timeout_s = timeout_s
        self.css_selector = css_selector

    def __next__(self) -> str:
        if self.currentPage > self.limit:
            raise StopIteration
        
        if self.currentPage > 1:
            try:
                logging.debug(f"Navigating to page {self.currentPage}")
                self.driver.nextPage(self.css_selector, self.timeout_s)
            except StopIteration:
                raise StopIteration
        
        html = self.driver.get_html()
        self.currentPage += 1
        
        return html

    def __iter__(self):
        return self
