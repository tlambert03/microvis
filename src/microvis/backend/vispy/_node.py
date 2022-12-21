from __future__ import annotations

from typing import Any

from vispy import scene
from vispy.visuals.transforms import MatrixTransform, NullTransform

from microvis.core import Transform
from microvis.core.nodes import node as core_node


class Node(core_node.NodeBackend):
    """Node adapter for Vispy Backend."""

    _native: scene.VisualNode

    def _viz_get_native(self) -> Any:
        return self._native

    def _viz_set_name(self, arg: str) -> None:
        self._native.name = arg

    def _viz_set_parent(self, arg: core_node.Node | None) -> None:
        if arg is None:
            self._native.parent = None
        elif isinstance(arg.native_objects, scene.Node):
            self._native.parent = arg.native_objects
        else:
            raise TypeError("Parent must be a Node")

    def _viz_set_children(self, arg: list[core_node.Node]) -> None:
        raise NotImplementedError

    def _viz_set_visible(self, arg: bool) -> None:
        self._native.visible = arg

    def _viz_set_opacity(self, arg: float) -> None:
        self._native.opacity = arg

    def _viz_set_order(self, arg: int) -> None:
        self._native.order = arg

    def _viz_set_interactive(self, arg: bool) -> None:
        self._native.interactive = arg

    def _viz_set_transform(self, arg: Transform) -> None:
        T = NullTransform() if arg.is_null() else MatrixTransform(arg.matrix)
        self._native.transform = T

    def _viz_add_node(self, node: core_node.Node) -> None:
        if not isinstance(node.native_objects, scene.Node):
            raise TypeError("Node must be a Vispy Node")
        node.native_objects.parent = self._native
