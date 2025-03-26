from typing import TypedDict

from dtypes.selector import Selector


class SourceDict(TypedDict):
    url: str
    trigger_ai: bool
    trigger_africa: bool
    selectors: Selector
