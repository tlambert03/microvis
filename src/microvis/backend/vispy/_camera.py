from __future__ import annotations

from typing import Any, cast

import numpy as np
from vispy import scene
from vispy.util.event import Event

from microvis._types import CameraType
from microvis.core.nodes import camera

from ._node import Node


class Camera(Node, camera.CameraAdaptorProtocol):
    """Adaptor between core camera and vispy camera."""

    _core_camera: camera.Camera
    _vispy_node: scene.cameras.BaseCamera

    def __init__(self, camera: camera.Camera, **backend_kwargs: Any) -> None:
        self._core_camera = camera
        backend_kwargs.setdefault("flip", (0, 1, 0))  # Add to core schema?
        # backend_kwargs.setdefault("aspect", 1)
        cam = scene.cameras.make_camera(str(camera.type), **backend_kwargs)
        self._vispy_camera = cam

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

    def _vis_cleanup(self) -> None:
        """Disconnects camera events."""
        self._vispy_camera.events.disconnect()

    def _view_size(self) -> tuple[float, float] | None:
        """Return the size of first parent viewbox in pixels."""
        obj = self._vispy_node
        while (obj := obj.parent) is not None:
            if isinstance(obj, scene.ViewBox):
                return cast("tuple[float, float]", obj.size)
        return None

    @property
    def _vispy_camera(self) -> scene.cameras.BaseCamera:
        return self._vispy_node

    @_vispy_camera.setter
    def _vispy_camera(self, arg: scene.cameras.BaseCamera) -> None:
        if hasattr(self, "_vispy_node"):
            self._vispy_node.events.disconnect()
        # this event should be a good catchall covering all relevant updates
        # for both ArcBallCamera and PanZoomCamera
        # fixme: this event not actually emitted lol, thx vispy
        # napari updates the camera whenever the canvas is redrawn, hopefully
        # we can avoid that...
        arg.events.transform_change.connect(self._on_vispy_camera_transform_change)
        self._vispy_node = arg

    def _on_vispy_camera_transform_change(self, event: Event = None) -> None:
        with self._core_camera.events.blocked():
            self._core_camera.center = self._vispy_camera.center[::-1]
            # todo: figure out zoom logic
            # see https://github.com/napari/napari/blob/ee94c35c04674ddc8e89ed63ac7674c27fa8fc6c/napari/_vispy/camera.py#L95-L123
