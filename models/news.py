from utils.checker import Checker


class NewsAdd:
    def __init__(
        self,
        authorId: int | None,
        title: str,
        url: str,
        sourceId: int,
        body: str,
        postDate: str,
        imageUrl: str | None,
    ) -> None:
        if Checker.is_date(title):
            raise ValueError("Title cannot be a date")
        if Checker.is_date(url):
            raise ValueError("URL cannot be a date")
        if Checker.is_date(body):
            raise ValueError("Body cannot be a date")
        if not title.strip():
            raise ValueError("Title cannot be empty")
        if not body.strip():
            raise ValueError("Body cannot be empty")
            
        if not Checker.is_date(postDate):
            raise ValueError(f"Invalid post date: '{postDate}'")

        self.authorId = authorId
        self.title = title
        self.url = url
        self.sourceId = sourceId
        self.body = body
        self.postDate = postDate
        self.imageUrl = imageUrl
