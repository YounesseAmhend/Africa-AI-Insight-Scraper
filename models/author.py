from utils.checker import Checker


class Author:

    def __init__(
        self,
        name: str | None,
        url: str | None,
        image_url: str | None,
    ):
        self.name = name
        self.url = url
        self.image_url = image_url