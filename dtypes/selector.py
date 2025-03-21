from typing import TypedDict
from .author import Author

class Selector(TypedDict):
    title: str
    link: str 
    next_button: str | None
    author: Author | None
    load_more_button: str | None # Some website don't have it 
    # body: str
    # event_date: str
    # post_date: str