class Source:

    def __init__(
        self,
        id: int,
        url: str,
        selector: dict,
        triggerAfrica: bool,
        triggerAi: bool,
        createdAt: str,
        updateAt: str | None,
    ):
        self.id = id
        self.url = url
        self.selector = selector
        self.triggerAfrica = triggerAfrica
        self.triggerAi = triggerAi
        self.createdAt = createdAt
        self.updatedAt = updateAt
