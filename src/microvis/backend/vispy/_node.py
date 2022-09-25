from __future__ import annotations

from typing import TYPE_CHECKING
from ...core.nodes import node as core_node

if TYPE_CHECKING:
    from vispy import scene


class Node(core_node.NodeBackend):
    """Node adapter for Vispy Backend."""

    _native: scene.VisualNode

    def _viz_set_name(self, arg: str) -> None:
        self._native.name = arg

    def _viz_set_parent(self, arg: core_node.Node | None) -> None:
        self._native.parent = arg.native if arg else None

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
