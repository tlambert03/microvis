from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygfx

from microvis import core

from ._node import Node

if TYPE_CHECKING:
    from microvis import _types

    from ._camera import Camera as CameraAdaptor


class View(Node, core.view.ViewAdaptorProtocol):
    """View interface for pygfx Backend."""

    # _native: scene.ViewBox
    # TODO: i think pygfx doesn't see a view as part of the scene like vispy does
    _camera: CameraAdaptor

    def __init__(self, view: core.View, **backend_kwargs: Any) -> None:
        # FIXME:  hardcoded camera and scene
        self.scene = pygfx.Scene()

    # XXX: both of these methods deserve scrutiny, and fixing :)
    def _vis_set_camera(self, cam: core.Camera) -> None:
        if not isinstance(cam.native, pygfx.Camera):
            raise TypeError(f"cam must be a pygfx.Camera, got {type(cam.native)}")
        self._camera = cam.backend_adaptor()

    def _vis_set_scene(self, scene: core.Scene) -> None:
        # XXX: Tricky!  this call to scene.native actually has the side effect of
        # creating the backend adaptor for the scene!  That needs to be more explicit.
        if not isinstance(scene.native, pygfx.Scene):
            raise TypeError("Scene must be a pygfx.Scene")
        self.scene = scene.native

    def _vis_set_position(self, arg: tuple[float, float]) -> None:
        raise NotImplementedError

    def _vis_set_size(self, arg: tuple[float, float] | None) -> None:
        raise NotImplementedError

    def _vis_set_background_color(self, arg: _types.Color | None) -> None:
        raise NotImplementedError

    def _vis_set_border_width(self, arg: float) -> None:
        raise NotImplementedError

    def _vis_set_border_color(self, arg: _types.Color | None) -> None:
        raise NotImplementedError

    def _vis_set_padding(self, arg: int) -> None:
        raise NotImplementedError

    def _vis_set_margin(self, arg: int) -> None:
        raise NotImplementedError

    def _visit(self, viewport: pygfx.Viewport) -> None:
        viewport.render(self.scene, self._camera._native)
        self._camera.update_controller()
