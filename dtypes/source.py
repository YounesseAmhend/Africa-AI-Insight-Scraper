from typing import TypedDict

from dtypes.selector import Selector

class Source(TypedDict):
    url: str
    trigger_words: list[str]
    trigger_phrases: list[str]
    selectors: Selector
    