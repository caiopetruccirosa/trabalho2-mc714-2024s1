# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: node_service.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12node_service.proto\x12\x0cnode_service\"\x1e\n\x0bNodeRequest\x12\x0f\n\x07node_id\x18\x01 \x01(\x05\"\x0e\n\x0cNodeResponse2\xf5\x01\n\x04Node\x12\x46\n\x0bRunElection\x12\x19.node_service.NodeRequest\x1a\x1a.node_service.NodeResponse\"\x00\x12T\n\x19ReceiveCoordinatorMessage\x12\x19.node_service.NodeRequest\x1a\x1a.node_service.NodeResponse\"\x00\x12O\n\x14GetCoordinatorStatus\x12\x19.node_service.NodeRequest\x1a\x1a.node_service.NodeResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'node_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_NODEREQUEST']._serialized_start=36
  _globals['_NODEREQUEST']._serialized_end=66
  _globals['_NODERESPONSE']._serialized_start=68
  _globals['_NODERESPONSE']._serialized_end=82
  _globals['_NODE']._serialized_start=85
  _globals['_NODE']._serialized_end=330
# @@protoc_insertion_point(module_scope)
