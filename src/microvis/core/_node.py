from __future__ import annotations

from .. import schema
from .._protocols import FrontEndFor, NodeBackend
from .._logs import logger


class Node(FrontEndFor[NodeBackend], schema.Node):
    def add(self, node: Node) -> None:
        logger.debug(f'Adding node {node} to {self}')
        self._backend._viz_add_node(node)
        self.children.append(node)
