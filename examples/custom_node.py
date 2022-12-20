"""An example of creating a custom node that can be added to a scene."""
from typing import Any

import numpy as np
from vispy import scene

from microvis import Canvas
from microvis.backend import vispy
from microvis.core.nodes._data import DataNode


# here, we're creating a custom node that works for vispy, so extending
# vispy.Node is easeiest approach
class CustomBackend(vispy.Node):
    def __init__(self, obj: "CustomNode", **backend_kwargs: Any) -> None:
        self._native = scene.Markers(pos=obj.data_raw, size=obj.size, **backend_kwargs)

    def _viz_set_data(self, data: Any) -> None:
        self._native.set_data(pos=data)

    def _viz_set_size(self, size: int) -> None:
        self._native.set_data(pos=self._native._data["a_position"], size=size)


# DataNode is the core class that all data nodes inherit from
class CustomNode(DataNode):
    # to provide a custom object, provide a backend object for each backend
    # that you want to support
    _backend_lookup = {"vispy": CustomBackend}

    # this is a pydantic-style model.  all attributes will trigger a
    # _viz_set_* method on the backend object (which must be implemented)
    size: int = 10


c = Canvas()
v = c.add_view()

custom_node = CustomNode(np.random.rand(10, 2))
v.add_node(custom_node)

c.show()

# from qtpy.QtWidgets import QApplication
# QApplication.instance().exec_()
