from typing import TypedDict


class Author(TypedDict):
    name: str
    link: str | None
    image_url: str | None