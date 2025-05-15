class Statistics:

    def __init__(
        self,
        id: int,
        name: str,
        stats: dict,
        updateAt: str | None,
    ):
        self.id = id
        self.name = name
        self.stats = stats
        self.updatedAt = updateAt
