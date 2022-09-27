from typing import Any, cast

from vispy.scene.subscene import SubScene
from vispy.visuals.filters import Clipper

from ... import core
from ._node import Node


# TODO: combine this logic with FrontEndFor
def _create_vispy_node(obj: core.nodes.Node) -> Node:
    """Create a vispy Node from a core.Node."""
    if "vispy" in obj._backend_lookup:
        cls = obj._backend_lookup["vispy"]
    else:
        from .. import vispy

        cls = getattr(vispy, obj.__class__.__name__)
    return cast("Node", cls(obj))


class Scene(Node):
    def __init__(self, scene: core.Scene, **backend_kwargs: Any) -> None:
        self._native = SubScene(**backend_kwargs)
        self._native._clipper = Clipper()
        self._native.clip_children = True

        for node in scene.children:
            if not node.has_backend:
                node._backend = _create_vispy_node(node)
            self._viz_add_node(node)
