from dtypes.author import Author


from typing import TypedDict


class NewsDict(TypedDict):
    title: str
    link: str
    author: Author | None
    body: str
    event_date: str | None
    post_date: str | None
    image_url: str | None
