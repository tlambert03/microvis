from __future__ import annotations

from typing import Any

import pygfx

from microvis._types import CameraType
from microvis.core.nodes import camera

from ._node import Node


class Camera(Node, camera.CameraAdaptorProtocol):
    """Adaptor for pygfx camera."""

    _native: pygfx.Camera

    def __init__(self, camera: camera.Camera, **backend_kwargs: Any) -> None:
        if camera.type == CameraType.PANZOOM:
            self._native = pygfx.OrthographicCamera(**backend_kwargs)
            self.controller = pygfx.PanZoomController(self._native.position.clone())
        elif camera.type == CameraType.ARCBALL:
            self._native = pygfx.PerspectiveCamera(**backend_kwargs)
            self.controller = pygfx.OrbitOrthoController(self._native.position.clone())

        # FIXME: hardcoded
        self._native.scale.y = -1

    def _vis_set_zoom(self, zoom: float) -> None:
        raise NotImplementedError

    def _vis_set_center(self, arg: tuple[float, ...]) -> None:
        raise NotImplementedError

    def _vis_set_type(self, arg: CameraType) -> None:
        raise NotImplementedError

    def _view_size(self) -> tuple[float, float] | None:
        """Return the size of first parent viewbox in pixels."""
        raise NotImplementedError

    def update_controller(self) -> None:
        # This is called by the View Adaptor in the `_visit` method
        # ... which is in turn called by the Canvas backend adaptor's `_animate` method
        # i.e. the main render loop.
        self.controller.update_camera(self._native)

    def set_viewport(self, viewport: pygfx.Viewport) -> None:
        # This is used by the Canvas backend adaptor...
        # and should perhaps be moved to the View Adaptor
        self.controller.add_default_event_handlers(viewport, self._native)
