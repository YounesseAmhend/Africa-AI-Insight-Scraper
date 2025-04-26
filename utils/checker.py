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
    def get_date(date_string: str) -> datetime.datetime | None:

        date_string = __class__.clean_date(date_string)

        date_formats = [
            "%A, %B %d, %Y",  # Weekday, Full month name, day, year
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
            "%d-%b-%Y",  # Day-Month(abbr)-Year
            "%d-%B-%Y",  # Day-Month(full)-Year
            "%Y %b %d",  # Year Month(abbr) Day
            "%Y %B %d",  # Year Month(full) Day
            "%b %d %Y",  # Month(abbr) Day Year
            "%B %d %Y",  # Month(full) Day Year
            "%Y/%b/%d",  # Year/Month(abbr)/Day
            "%Y/%B/%d",  # Year/Month(full)/Day
            "%d %m %Y",  # Day Month Year (numeric)
            "%Y %m %d",  # Year Month Day (numeric)
            "%m %d %Y",  # Month Day Year (numeric)
            "%Y-%m-%d %H:%M",  # ISO format with time
            "%Y/%m/%d %H:%M",  # Year/month/day with time
            "%d-%m-%Y %H:%M",  # Day-month-year with time
            "%m/%d/%Y %I:%M %p",  # US format with 12-hour time
            "%d/%m/%Y %H:%M",  # European format with time
            "%Y%m%d%H%M",  # Compact ISO format with time
            "%Y-%m-%dT%H:%M:%S",  # ISO 8601 format
            "%Y-%m-%dT%H:%M:%SZ",  # ISO 8601 with Zulu time
            "%a, %d %b %Y %H:%M:%S %Z",  # RFC 822 format
            "%A, %d %B %Y %H:%M:%S",  # Full weekday, day, month, year with time
            "%Y-%m-%d %H:%M:%S.%f",  # ISO format with microseconds
            "%Y-%m-%d %H:%M:%S %Z",  # ISO format with timezone
            "%Y-%m-%d %H:%M:%S %z",  # ISO format with UTC offset
            "%Y-%m-%dT%H:%M:%S.%f%z",  # ISO 8601 with microseconds and UTC offset
            "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO 8601 with microseconds and Zulu time
            "%a %b %d %H:%M:%S %Y",  # Unix date format
            "%a %b %d %H:%M:%S %Z %Y",  # Unix date format with timezone
            "%Y年%m月%d日 %H:%M:%S",  # Chinese format with time
            "%Y년 %m월 %d일 %H:%M:%S",  # Korean format with time
            "%d/%m/%Y %H:%M:%S %Z",  # European format with timezone
            "%m/%d/%Y %I:%M:%S %p %Z",  # US format with 12-hour time and timezone
            "%Y%m%d%H%M%S",  # Compact ISO format with seconds
            "%Y%m%d%H%M%S%z",  # Compact ISO format with seconds and UTC offset
            "%Y%m%d%H%M%S.%f",  # Compact ISO format with seconds and microseconds
            "%Y%m%d%H%M%S.%f%z",  # Compact ISO format with seconds, microseconds and UTC offset
            "%Y年%m月%d日 %H:%M:%S",  # Chinese format with time
            "%Y년 %m월 %d일 %H:%M:%S",  # Korean format with time
            "%d/%m/%Y %H:%M:%S %Z",  # European format with timezone
            "%m/%d/%Y %I:%M:%S %p %Z",  # US format with 12-hour time and timezone
            "%Y%m%d%H%M%S",  # Compact ISO format with seconds
            "%Y%m%d%H%M%S%z",  # Compact ISO format with seconds and UTC offset
            "%Y%m%d%H%M%S.%f",  # Compact ISO format with seconds and microseconds
            "%d %B %Y %H:%M:%S",  # French format with full month name
            "%d %b %Y %H:%M:%S",  # French format with abbreviated month name
            "%Y-%m-%d %H:%M:%S",  # ISO format with time
            "%Y/%m/%d %H:%M:%S",  # Year/month/day with time
            "%d-%m-%Y %H:%M:%S",  # Day-month-year with time
            "%m/%d/%Y %I:%M %p",  # US format with 12-hour time
            "%d/%m/%Y %H:%M:%S",  # European format with time
            "%Y%m%d%H%M%S",  # Compact ISO format with time
            "%Y-%m-%dT%H:%M:%S",  # ISO 8601 format
            "%Y-%m-%dT%H:%M:%SZ",  # ISO 8601 with Zulu time
            "%a, %d %b %Y %H:%M:%S %Z",  # RFC 822 format
            "%A, %d %B %Y %H:%M:%S",  # Full weekday, day, month, year with time
            "%Y-%m-%d %H:%M:%S.%f",  # ISO format with microseconds
            "%Y-%m-%d %H:%M:%S %Z",  # ISO format with timezone
            "%Y-%m-%d %H:%M:%S %z",  # ISO format with UTC offset
            "%Y-%m-%dT%H:%M:%S.%f%z",  # ISO 8601 with microseconds and UTC offset
            "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO 8601 with microseconds and Zulu time
            "%a %b %d %H:%M:%S %Y",  # Unix date format
            "%a %b %d %H:%M:%S %Z %Y",  # Unix date format with timezone
            "%Y年%m月%d日 %H:%M:%S",  # Chinese format with time
            "%Y년 %m월 %d일 %H:%M:%S",  # Korean format with time
            "%d/%m/%Y %H:%M:%S %Z",  # European format with timezone
            "%m/%d/%Y %I:%M:%S %p %Z",  # US format with 12-hour time and timezone
            "%Y%m%d%H%M%S",  # Compact ISO format with seconds
            "%Y%m%d%H%M%S%z",  # Compact ISO format with seconds and UTC offset
            "%Y%m%d%H%M%S.%f",  # Compact ISO format with seconds and microseconds
            "%Y%m%d%H%M%S.%f%z",  # Compact ISO format with seconds, microseconds and UTC offset
            "%d %B %Y %H:%M:%S",  # French format with full month name
            "%d %b %Y %H:%M:%S",  # French format with abbreviated month name
            "%Y-%m-%d %H:%M:%S",  # ISO format with time
            "%Y/%m/%d %H:%M:%S",  # Year/month/day with time
            "%d-%m-%Y %H:%M:%S",  # Day-month-year with time
            "%m/%d/%Y %I:%M %p",  # US format with 12-hour time
            "%d/%m/%Y %H:%M:%S",  # European format with time
            "%Y%m%d%H%M%S",  # Compact ISO format with time
            "%Y-%m-%dT%H:%M:%S",  # ISO 8601 format
            "%Y-%m-%dT%H:%M:%SZ",  # ISO 8601 with Zulu time
            "%a, %d %b %Y %H:%M:%S %Z",  # RFC 822 format
            "%A, %d %B %Y %H:%M:%S",  # Full weekday, day, month, year with time
            "%Y-%m-%d %H:%M:%S.%f",  # ISO format with microseconds
            "%Y-%m-%d %H:%M:%S %Z",  # ISO format with timezone
            "%Y-%m-%d %H:%M:%S %z",  # ISO format with UTC offset
            "%Y-%m-%dT%H:%M:%S.%f%z",  # ISO 8601 with microseconds and UTC offset
            "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO 8601 with microseconds and Zulu time
            "%a %b %d %H:%M:%S %Y",  # Unix date format
            "%a %b %d %H:%M:%S %Z %Y",  # Unix date format with timezone
            "%Y年%m月%d日 %H:%M:%S",  # Chinese format with time
            "%Y년 %m월 %d일 %H:%M:%S",  # Korean format with time
            "%d/%m/%Y %H:%M:%S %Z",  # European format with timezone
            "%m/%d/%Y %I:%M:%S %p %Z",  # US format with 12-hour time and timezone
            "%Y%m%d%H%M%S",  # Compact ISO format with seconds
            "%Y%m%d%H%M%S%z",  # Compact ISO format with seconds and UTC offset
            "%Y%m%d%H%M%S.%f",  # Compact ISO format with seconds and microseconds
            "%Y%m%d%H%M%S.%f%z",  # Compact ISO format with seconds, microseconds and UTC offset
            "%d %B %Y %H:%M:%S",  # French format with full month name
            "%d %b %Y %H:%M:%S",  # French format with abbreviated month name
            "%Y-%m-%d %H:%M:%S",  # ISO format with time
            "%Y/%m/%d %H:%M:%S",  # Year/month/day with time
            "%d-%m-%Y %H:%M:%S",  # Day-month-year with time
            "%m/%d/%Y %I:%M %p",  # US format with 12-hour time
            "%d/%m/%Y %H:%M:%S",  # European format with time
            "%Y%m%d%H%M%S",  # Compact ISO format with time
            "%Y-%m-%dT%H:%M:%S",  # ISO 8601 format
            "%Y-%m-%dT%H:%M:%SZ",  # ISO 8601 with Zulu time
            "%a, %d %b %Y %H:%M:%S %Z",  # RFC 822 format
            "%A, %d %B %Y %H:%M:%S",  # Full weekday, day, month, year with time
            "%Y-%m-%d %H:%M:%S.%f",  # ISO format with microseconds
            "%Y-%m-%d %H:%M:%S %Z",  # ISO format with timezone
            "%Y-%m-%d %H:%M:%S %z",  # ISO format with UTC offset
            "%Y-%m-%dT%H:%M:%S.%f%z",  # ISO 8601 with microseconds and UTC offset
            "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO 8601 with microseconds and Zulu time
            "%a %b %d %H:%M:%S %Y",  # Unix date format
            "%a %b %d %H:%M:%S %Z %Y",  # Unix date format with timezone
            "%Y年%m月%d日 %H:%M:%S",  # Chinese format with time
        ]
        # Try parsing with each format
        for fmt in date_formats:
            try:
                return datetime.datetime.strptime(date_string.strip(), fmt)
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
            "منشور:",  # Arabic for "Post:"
            "مقالة:",  # Arabic for "Article:"
            "أخبار:",  # Arabic for "News:"
            "حدث:",    # Arabic for "Event:"
            "تاريخ النشر:",  # Arabic for "Publication date:"
            "تاريخ:",  # Arabic for "Date:"
            "Posté:",  # French for "Posted:"
            "Article:",  # French for "Article:"
            "Nouvelles:",  # French for "News:"
            "Événement:",  # French for "Event:"
            "Date de publication:",  # French for "Publication date:"
            "Date:",  # French for "Date:"
            "Publié:",  # French for "Published:"
            "Mis à jour:",  # French for "Updated:"
            "Créé:",  # French for "Created:"
            "Dernière mise à jour:",  # French for "Last updated:"
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
        except Exception:
            return False
