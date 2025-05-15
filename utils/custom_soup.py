from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup, Tag
from utils.checker import Checker


class CustomSoup:

    def __init__(
        self,
        html: str,
    ) -> None:
        self.soup = BeautifulSoup(html, "html.parser")

    def select_text(self, css_selector: str | None) -> str | None:
        """
        Select text from HTML using CSS selector

        Args:
            css_selector: CSS selector string to find element

        Returns:
            Text content of the element if found, None otherwise
        """
        if css_selector is None:
            return None
        element = self.soup.select_one(css_selector)
        return element.get_text().strip() if element else None
    
    def select_tag(self, css_selector: str | None) -> Tag | None:
        """
        Select text from HTML using CSS selector

        Args:
            css_selector: CSS selector string to find element

        Returns:
            Text content of the element if found, None otherwise
        """
        if css_selector is None:
            return None
        element = self.soup.select_one(css_selector)
        return element if element else None


    def select_date(self, css_selector: str | None) -> datetime | None:
        """
        Select and parse date from HTML using CSS selector

        Args:
            css_selector: CSS selector string to find element

        Returns:
            Parsed datetime object if valid date found, None otherwise
        """
        if css_selector is None:
            return None
        element = self.soup.select_one(css_selector)
        if element:
            date_text = element.get_text().strip()
            return Checker.get_date(date_text)
        return None

    def select_url(
        self,
        base_url: str,
        css_selector: str | None,
    ) -> str | None:
        """
        Select URL from HTML using CSS selector

        Args:
            css_selector: CSS selector string to find element

        Returns:
            URL from href attribute (for <a> tags) or src attribute (for <img> tags) if found, None otherwise
        """
        if css_selector is None:
            return None
        element = self.soup.select_one(css_selector)
        if element and element.name == "a":
            attr = (
                "href"
                if element.name == "a"
                else "src" if element.name == "img" else None
            )
            if attr:
                url = element.get(attr)
                if url:
                    return __class__.resolve_relative_url(base_url, str(url))

        return None

    @staticmethod
    def resolve_relative_url(
        base_url: str,
        url_fragment: str | list[str],
    ) -> str:
        if isinstance(url_fragment, list):
            url_fragment = "".join(
                url_fragment
            )  # If the URL fragment is too long it gets divided into a list so we need to join it back together

        if url_fragment and url_fragment.startswith("/"):
            parsed_url = urlparse(base_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            url_fragment = f"{base_url}{url_fragment}"

        return __class__.correct_url(url_fragment)

    @staticmethod
    def correct_url(
        url: str,
    ) -> str:
        parts = url.split("//", 2)  # Split into scheme and the rest
        if len(parts) == 3 and parts[1] in parts[2]:  # Detect duplicate domain
            return f"{parts[0]}//{parts[2]}"  # Keep only one domain occurrence
        return url
