from __future__ import annotations

from typing import Any

from vispy import scene
from vispy.visuals.transforms import MatrixTransform, NullTransform

from microvis.core import Transform
from microvis.core.nodes import node as core_node


class Node(core_node.NodeBackend):
    """Node adaptor for Vispy Backend."""

    _vispy_node: scene.VisualNode

    def _vis_get_native(self) -> Any:
        return self._vispy_node

    def _vis_set_name(self, arg: str) -> None:
        self._vispy_node.name = arg

    def _vis_set_parent(self, arg: core_node.Node | None) -> None:
        if arg is None:
            self._vispy_node.parent = None
        elif isinstance(arg.native, scene.Node):
            self._vispy_node.parent = arg.native
        else:
            raise TypeError("Parent must be a Node")

    def _vis_set_children(self, arg: list[core_node.Node]) -> None:
        raise NotImplementedError

    def _vis_set_visible(self, arg: bool) -> None:
        self._vispy_node.visible = arg

    def _vis_set_opacity(self, arg: float) -> None:
        self._vispy_node.opacity = arg

    def _vis_set_order(self, arg: int) -> None:
        self._vispy_node.order = arg

    def _vis_set_interactive(self, arg: bool) -> None:
        self._vispy_node.interactive = arg

    def _vis_set_transform(self, arg: Transform) -> None:
        T = NullTransform() if arg.is_null() else MatrixTransform(arg.matrix)
        self._vispy_node.transform = T

    def _vis_add_node(self, node: core_node.Node) -> None:
        if not isinstance(node.native, scene.Node):
            raise TypeError("Node must be a Vispy Node")
        node.native.parent = self._vispy_node
