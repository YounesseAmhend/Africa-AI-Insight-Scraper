from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AuthorResponse(_message.Message):
    __slots__ = ("name", "url")
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    name: str
    url: str
    def __init__(self, name: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...

class AuthorRequest(_message.Message):
    __slots__ = ("name", "url")
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    name: str
    url: str
    def __init__(self, name: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...
