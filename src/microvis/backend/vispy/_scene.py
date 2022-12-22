from typing import Any

from vispy.scene.subscene import SubScene
from vispy.visuals.filters import Clipper

from microvis import core

from ._node import Node


class Scene(Node):
    def __init__(self, scene: core.Scene, **backend_kwargs: Any) -> None:
        self._vispy_node = SubScene(**backend_kwargs)
        self._vispy_node._clipper = Clipper()
        self._vispy_node.clip_children = True

        for node in scene.children:
            node.backend_adaptor()  # create backend adaptor if it doesn't exist
            self._viz_add_node(node)
