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
        self.authorId = authorId
        self.title = title
        self.url = url
        self.sourceId = sourceId
        self.body = body
        self.postDate = postDate
        self.imageUrl = imageUrl
