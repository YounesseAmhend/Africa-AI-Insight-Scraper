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

class SourceUpdate:
    def __init__(
        self,
        url: str,
        containsAiContent: bool,
        containsAfricaContent: bool,
    ):
        self.url = url
        self.containsAiContent = containsAiContent
        self.containsAfricaContent = containsAfricaContent