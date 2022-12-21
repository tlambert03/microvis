from typing import Any

from pygfx.objects import Scene as _Scene

from microvis import core

from ._node import Node


class Scene(Node):
    def __init__(self, scene: core.Scene, **backend_kwargs: Any) -> None:
        self._native = _Scene(
            visible=scene.visible, render_order=scene.order, **backend_kwargs
        )

        for node in scene.children:
            node.backend_adaptor()  # create backend adaptor if it doesn't exist
            self._viz_add_node(node)
