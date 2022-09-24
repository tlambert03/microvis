from .. import schema
from .._protocols import FrontEndFor, NodeBackend


class Node(FrontEndFor[NodeBackend], schema.Node):
    ...
