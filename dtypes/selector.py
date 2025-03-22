from typing import TypedDict
from .author import Author

class Selector(TypedDict):
    title: str
    link: str 
    load_more_button: str | None # Some website don't have it 
    next_button: str | None


class PageSelector(TypedDict):
    author: Author | None
    body: str
    event_date: str | None
    post_date: str | None
