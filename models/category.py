class Category:

    def __init__(
        self,
        id: int,
        name: str,
        updateAt: str | None,
    ):
        self.id = id
        self.name = name
        self.updatedAt = updateAt
