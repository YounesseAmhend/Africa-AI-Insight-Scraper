# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: rpc/services/source.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'rpc/services/source.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19rpc/services/source.proto\x12\x06source\"V\n\rSourceRequest\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x19\n\x11\x63ontainsAiContent\x18\x02 \x01(\x08\x12\x1d\n\x15\x63ontainsAfricaContent\x18\x03 \x01(\x08\"\xd2\x01\n\x06Source\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0b\n\x03url\x18\x02 \x01(\t\x12.\n\x08selector\x18\x03 \x03(\x0b\x32\x1c.source.Source.SelectorEntry\x12\x15\n\rtriggerAfrica\x18\x04 \x01(\x08\x12\x11\n\ttriggerAi\x18\x05 \x01(\x08\x12\x11\n\tcreatedAt\x18\x06 \x01(\t\x12\x11\n\tupdatedAt\x18\x07 \x01(\t\x1a/\n\rSelectorEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"!\n\x0eSourceResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"\x0f\n\rScrapeRequest\"!\n\x0eScrapeResponse\x12\x0f\n\x07message\x18\x01 \x01(\t2\x88\x01\n\rSourceService\x12<\n\taddSource\x12\x15.source.SourceRequest\x1a\x16.source.SourceResponse\"\x00\x12\x39\n\x06scrape\x12\x15.source.ScrapeRequest\x1a\x16.source.ScrapeResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'rpc.services.source_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_SOURCE_SELECTORENTRY']._loaded_options = None
  _globals['_SOURCE_SELECTORENTRY']._serialized_options = b'8\001'
  _globals['_SOURCEREQUEST']._serialized_start=37
  _globals['_SOURCEREQUEST']._serialized_end=123
  _globals['_SOURCE']._serialized_start=126
  _globals['_SOURCE']._serialized_end=336
  _globals['_SOURCE_SELECTORENTRY']._serialized_start=289
  _globals['_SOURCE_SELECTORENTRY']._serialized_end=336
  _globals['_SOURCERESPONSE']._serialized_start=338
  _globals['_SOURCERESPONSE']._serialized_end=371
  _globals['_SCRAPEREQUEST']._serialized_start=373
  _globals['_SCRAPEREQUEST']._serialized_end=388
  _globals['_SCRAPERESPONSE']._serialized_start=390
  _globals['_SCRAPERESPONSE']._serialized_end=423
  _globals['_SOURCESERVICE']._serialized_start=426
  _globals['_SOURCESERVICE']._serialized_end=562
# @@protoc_insertion_point(module_scope)
