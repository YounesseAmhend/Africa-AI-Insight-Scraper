from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AuthorResponse(_message.Message):
    __slots__ = ("name", "url")
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    name: str
    url: str
    def __init__(self, name: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...

class NewsAddRequest(_message.Message):
    __slots__ = ("id", "sourceId", "title", "url", "authorId", "body", "eventDate", "postDate", "imageUrl")
    ID_FIELD_NUMBER: _ClassVar[int]
    SOURCEID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    AUTHORID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    EVENTDATE_FIELD_NUMBER: _ClassVar[int]
    POSTDATE_FIELD_NUMBER: _ClassVar[int]
    IMAGEURL_FIELD_NUMBER: _ClassVar[int]
    id: int
    sourceId: int
    title: str
    url: str
    authorId: int
    body: str
    eventDate: str
    postDate: str
    imageUrl: str
    def __init__(self, id: _Optional[int] = ..., sourceId: _Optional[int] = ..., title: _Optional[str] = ..., url: _Optional[str] = ..., authorId: _Optional[int] = ..., body: _Optional[str] = ..., eventDate: _Optional[str] = ..., postDate: _Optional[str] = ..., imageUrl: _Optional[str] = ...) -> None: ...

class NewsResponse(_message.Message):
    __slots__ = ("id", "sourceUrl", "title", "url", "author", "body", "eventDate", "postDate", "imageUrl")
    ID_FIELD_NUMBER: _ClassVar[int]
    SOURCEURL_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    EVENTDATE_FIELD_NUMBER: _ClassVar[int]
    POSTDATE_FIELD_NUMBER: _ClassVar[int]
    IMAGEURL_FIELD_NUMBER: _ClassVar[int]
    id: int
    sourceUrl: str
    title: str
    url: str
    author: AuthorResponse
    body: str
    eventDate: str
    postDate: str
    imageUrl: str
    def __init__(self, id: _Optional[int] = ..., sourceUrl: _Optional[str] = ..., title: _Optional[str] = ..., url: _Optional[str] = ..., author: _Optional[_Union[AuthorResponse, _Mapping]] = ..., body: _Optional[str] = ..., eventDate: _Optional[str] = ..., postDate: _Optional[str] = ..., imageUrl: _Optional[str] = ...) -> None: ...
