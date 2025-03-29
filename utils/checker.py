import datetime


class Checker:

    @staticmethod
    def is_date(value: str | None, can_be_none: bool = False) -> bool:
        """Check if a string is a valid date.
        
        Args:
            value: The string to check
            can_be_none: Whether None values should be considered valid
            
        Returns:
            bool: True if the string is a valid date or None and can_be_none is True
        """
        if value is None:
            return can_be_none
        return __class__.get_date(value) is not None

    @staticmethod
    def get_date(value: str) -> datetime.datetime | None:

        value = __class__.clean_date(value)

        date_formats = [
            "%B %d, %Y",  # Full month name, day, year
            "%Y-%m-%d",  # ISO format
            "%m/%d/%Y",  # US format
            "%d/%m/%Y",  # European format
            "%b %d, %Y",  # Month name, day, year
            "%B %d, %Y",  # Full month name, day, year
            "%Y/%m/%d",  # Year/month/day
            "%d-%m-%Y",  # Day-month-year
            "%Y.%m.%d",  # Year.month.day
            "%d %b %Y",  # Day Month(abbr) Year
            "%d %B %Y",  # Day Month(full) Year
            "%Y%m%d",    # Compact ISO format
            "%m-%d-%Y",  # US format with hyphens
            "%d.%m.%Y",  # European format with dots
            "%Y-%b-%d",  # Year-Month(abbr)-Day
            "%Y-%B-%d",  # Year-Month(full)-Day
            "%b %Y",     # Month(abbr) Year
            "%B %Y",     # Month(full) Year
            "%Y",        # Year only
            "%m/%Y",     # Month/Year
            "%Y-%m",     # Year-Month
        ]

        # Try parsing with each format
        for fmt in date_formats:
            try:
                return datetime.datetime.strptime(value, fmt)
            except ValueError:
                continue

    @staticmethod
    def clean_date(
        date: str,
    ) -> str:
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
            "On",
            "At",
            "Posted at",
            "Published at",
            "Last modified",
            "Modified on",
            "Modified",
            "Release date:",
            "Posted date:",
            "Publication date:",
            "Post date:",
            "Article date:",
            "News date:",
            "Event date:",
            "Posted by",
            "Published by",
            "Added on",
            "Added",
            "Posted -",
            "Published -",
            "Updated -",
            "Created -",
            "Date -",
            "Time -",
            "Posted:",
            "Published:",
            "Updated:",
            "Created:",
            "Last updated:",
            "Last modified:",
            "Modified:",
            "Release:",
            "Post:",
            "Article:",
            "News:",
            "Event:",
        ]
        for prefix in date_prefixes:
            date = date.replace(prefix, "").strip()

        return date

    @staticmethod
    def is_valid_url(url: str | None, can_be_none: bool = True) -> bool:
        """Check if a URL is valid and well-formed.

        Args:
            url: The URL string to validate

        Returns:
            bool: True if URL is valid, False otherwise
        """
        if url is None:
            return can_be_none

        # Basic checks for URL structure
        if not isinstance(url, str):
            return False

        if not url.startswith(('http://', 'https://')):
            return False

        # Check for basic URL components
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        except:
            return False
