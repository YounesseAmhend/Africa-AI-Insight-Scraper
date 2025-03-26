from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SourceRequest(_message.Message):
    __slots__ = ("url", "containsAiContent", "containsAfricaContent")
    URL_FIELD_NUMBER: _ClassVar[int]
    CONTAINSAICONTENT_FIELD_NUMBER: _ClassVar[int]
    CONTAINSAFRICACONTENT_FIELD_NUMBER: _ClassVar[int]
    url: str
    containsAiContent: bool
    containsAfricaContent: bool
    def __init__(self, url: _Optional[str] = ..., containsAiContent: bool = ..., containsAfricaContent: bool = ...) -> None: ...

class Source(_message.Message):
    __slots__ = ("id", "url", "selector", "triggerAfrica", "triggerAi", "createdAt", "updatedAt")
    class SelectorEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    SELECTOR_FIELD_NUMBER: _ClassVar[int]
    TRIGGERAFRICA_FIELD_NUMBER: _ClassVar[int]
    TRIGGERAI_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    id: int
    url: str
    selector: _containers.ScalarMap[str, str]
    triggerAfrica: bool
    triggerAi: bool
    createdAt: str
    updatedAt: str
    def __init__(self, id: _Optional[int] = ..., url: _Optional[str] = ..., selector: _Optional[_Mapping[str, str]] = ..., triggerAfrica: bool = ..., triggerAi: bool = ..., createdAt: _Optional[str] = ..., updatedAt: _Optional[str] = ...) -> None: ...

class SourceResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class ScrapeRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ScrapeResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...
