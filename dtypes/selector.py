from typing import TypedDict

from .author import Author

class Selector(TypedDict):
    title: str
    link: str
    author: Author
    load_more_button: str # Some website don't have it 
    # body: str
    # event_date: str
    # post_date: str