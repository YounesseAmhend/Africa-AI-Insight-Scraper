from dtypes.author_dict import AuthorDict


from typing import TypedDict


class NewsDict(TypedDict):
    title: str
    link: str
    author: AuthorDict | None
    body: str
    event_date: str | None
    post_date: str | None
    image_url: str | None
