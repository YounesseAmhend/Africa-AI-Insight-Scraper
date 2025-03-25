from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

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

class SourceResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...
