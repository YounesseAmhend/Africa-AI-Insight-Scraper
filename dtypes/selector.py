from typing import TypedDict
from .author import Author


class Selector(TypedDict):
    title: str
    link: str
    load_more_button: str | None  # Some website don't have it
    next_button: str | None
    author: Author | None
    body: str
    event_date: str | None
    post_date: str | None
    image_url: str | None


# this is just for the ai to convince him
class PageSelector(TypedDict):
    author: Author | None
    body: str
    event_date: str | None
    post_date: str | None
    image_url: str | None
