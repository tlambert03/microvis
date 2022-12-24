from __future__ import annotations

from typing import Any, cast

import numpy as np
from vispy import scene

from microvis._types import CameraType
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

    def _vis_set_zoom(self, zoom: float) -> None:
        if (view_size := self._view_size()) is None:
            return
        scale = np.array(view_size) / zoom
        if hasattr(self._vispy_node, "scale_factor"):
            self._vispy_node.scale_factor = np.min(scale)
        else:
            # Set view rectangle, as left, right, width, height
            corner = np.subtract(self._vispy_node.center[:2], scale / 2)
            self._vispy_node.rect = tuple(corner) + tuple(scale)

    def _vis_set_center(self, arg: tuple[float, ...]) -> None:
        self._vispy_node.center = arg[::-1]  # TODO
        self._vispy_node.view_changed()

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
