from __future__ import annotations

from typing import Any

from vispy import scene

from ...core.nodes import node as core_node


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
        else:
            assert isinstance(arg.native, scene.Node)
            self._native.parent = arg.native

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

    def _viz_set_transform(self, arg: core_node.Transform | None) -> None:
        raise NotImplementedError

    def _viz_add_node(self, node: core_node.Node) -> None:
        assert isinstance(node.native, scene.Node)
        node.native.parent = self._native
