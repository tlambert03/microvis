from __future__ import annotations

from typing import Any

from pygfx.geometries import Geometry
from pygfx.materials import Material
from pygfx.objects import WorldObject

from microvis.core import Transform
from microvis.core.nodes import node as core_node


class Node(core_node.NodeBackend):
    """Node adaptor for pygfx Backend."""

    _native: WorldObject
    _material: Material
    _geometry: Geometry
    _name: str

    def _viz_get_native(self) -> Any:
        return self._native

    def _viz_set_name(self, arg: str) -> None:
        # not sure pygfx has a name attribute...
        # TODO: for that matter... do we need a name attribute?
        # Could this be entirely managed on the model side/
        self._name = arg

    def _viz_set_parent(self, arg: core_node.Node | None) -> None:
        raise NotImplementedError

    def _viz_set_children(self, arg: list[core_node.Node]) -> None:
        # This is probably redundant with _viz_add_node
        # could maybe be a clear then add *arg
        raise NotImplementedError

    def _viz_set_visible(self, arg: bool) -> None:
        self._native.visible = arg

    def _viz_set_opacity(self, arg: float) -> None:
        self._material.opacity = arg

    def _viz_set_order(self, arg: int) -> None:
        self._native.render_order = arg

    def _viz_set_interactive(self, arg: bool) -> None:
        # this one requires knowledge of the controller
        raise NotImplementedError

    def _viz_set_transform(self, arg: Transform) -> None:
        self._native.matrix = arg.matrix  # TODO: check this

    def _viz_add_node(self, node: core_node.Node) -> None:
        self._native.add(node.native)
