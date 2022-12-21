"""An example of creating a custom node that can be added to a scene.

This is a very simple example, but it shows how to extend the base Node class (or
any of the other core classes) to create a custom node that can be added to a
scene.  It boils down to two steps:

1. Subclass `core.Node` and add class attributes with annotations defining your
   model (just like a dataclass or pydantic model).
2. Add a class attribute `BACKEND_ADAPTORS` that is a mapping of backend names to
   a backend adaptor classes (see next step for an explanation of what that is).
3. Implement one or more backend adaptor classes that implement the backend
   protocol for your new node.  Specifically, this means implementing `_viz_set_<name>`
   methods for each attribute in your model.

In the example below, a very simple "points" layer is created.  It has a single
attribute, `size`, that controls the size of the points. It is only implemented for
vispy.
"""
from typing import Any

import numpy as np
from vispy import scene

from microvis import Canvas
from microvis.backend import vispy
from microvis.core.nodes._data import DataNode


# here, we're creating a custom node that works for vispy, so extending the existing
# `microvis.backend.vispy.Node`` class is easiest approach.
# NOTE: since this likely means using private attributes of microvis' vispy backend,
# we should consider making a public API for this, or at least making certain attributes
# public (like, `native` here).
class CustomVispyAdaptor(vispy.Node):
    def __init__(self, obj: "CustomNode", **backend_kwargs: Any) -> None:
        self._native = scene.Markers(pos=obj.data_raw, size=obj.size, **backend_kwargs)

    def _vis_set_data(self, data: Any) -> None:
        self._native.set_data(pos=data)

    def _vis_set_size(self, size: int) -> None:
        self._native.set_data(pos=self._native._data["a_position"], size=size)


# DataNode is the core class that all data nodes inherit from
# Here was make a very simple model that just accepts a size attribute
class CustomNode(DataNode):
    # to provide a custom object, provide a backend object for each backend
    # that you want to support
    BACKEND_ADAPTORS = {"vispy": CustomVispyAdaptor}

    # this is a pydantic-style model.  all attributes will trigger a
    # _vis_set_* method on the backend object. (So `CustomVispyAdaptor` must have
    # a `_vis_set_size` method.)
    size: int = 10


if __name__ == "__main__":
    # Run it!
    from qtpy.QtWidgets import QApplication

    c = Canvas()
    v = c.add_view()

    custom_node = CustomNode(np.random.rand(20, 2))
    v.add_node(custom_node)

    c.show()

    QApplication.instance().exec_()
