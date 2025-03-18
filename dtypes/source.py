from typing import TypedDict

from dtypes.selector import Selector

class Source(TypedDict):
    url: str

    trigger_ai: bool
    trigger_africa: bool
    selectors: Selector
    