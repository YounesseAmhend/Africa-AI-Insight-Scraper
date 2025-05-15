from typing import TypedDict


class AuthorDict(TypedDict):
    name: str
    link: str | None
    image_url: str | None
