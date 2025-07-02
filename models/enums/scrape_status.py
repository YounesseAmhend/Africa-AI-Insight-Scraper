from enum import Enum


class ScrapeStatus(Enum):
    AVAILABLE = "available"
    FETCHING = "fetching"
    UNAVAILABLE = "unavailable"
