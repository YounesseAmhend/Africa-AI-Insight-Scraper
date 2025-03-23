from selenium.webdriver.edge.webdriver import WebDriver


from typing import Protocol


class CustomDriverProtocol(Protocol):
    driver: WebDriver

    def get_html(self) -> str: ...
    def nextPage(
        self,
        css_selector: str,
        timeout_s: float,
    ) -> None: ...
