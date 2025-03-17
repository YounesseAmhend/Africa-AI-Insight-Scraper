from typing import TypedDict

from .author import Author

class Selector(TypedDict):
    title: str
    link: str
    author: Author
    # body: str
    # event_date: str
    # post_date: str