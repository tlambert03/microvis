from __future__ import annotations

from typing import Any, cast

from vispy import scene

from microvis._types import CameraType
from microvis.core import Transform
from microvis.core.nodes import camera

from ._node import Node


class Camera(Node, camera.CameraAdaptorProtocol):
    """Adaptor for vispy camera."""

    _vispy_node: scene.cameras.BaseCamera

    def __init__(self, camera: camera.Camera, **backend_kwargs: Any) -> None:
        backend_kwargs.setdefault("flip", (0, 1, 0))  # Add to core schema?
        # backend_kwargs.setdefault("aspect", 1)
        cam = scene.cameras.make_camera(str(camera.type), **backend_kwargs)
        self._vispy_node = cam

    def _vis_set_projection_matrix(self, arg: Transform) -> None:
        ...

    #     self._vispy_node.view_changed()

    def _vis_set_type(self, arg: CameraType) -> None:
        if not isinstance(self._vispy_node.parent, scene.ViewBox):
            raise TypeError("Camera must be attached to a ViewBox")
        self._vispy_node.parent.camera = str(arg)

    def _view_size(self) -> tuple[float, float] | None:
        """Return the size of first parent viewbox in pixels."""
        obj = self._vispy_node
        while (obj := obj.parent) is not None:
            if isinstance(obj, scene.ViewBox):
                return cast("tuple[float, float]", obj.size)
        return None

    def _vis_set_range(self, margin: float) -> None:
        self._vispy_node.set_range(margin=margin)
