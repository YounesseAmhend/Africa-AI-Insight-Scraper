from typing import TypedDict

class Source(TypedDict):
    url: str
    trigger_words: list[str]
    trigger_phrases: list[str]
    selector: str