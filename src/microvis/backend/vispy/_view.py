from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vispy import scene
from vispy.scene import subscene

from ... import core
from ._camera import Camera
from ._node import Node
from ._scene import Scene
from ._util import pyd_color_to_vispy

if TYPE_CHECKING:
    from microvis import _types


class View(Node, core.view.ViewBackend):
    """View interface for Vispy Backend."""

    _native: scene.ViewBox

    def __init__(self, view: core.View, **backend_kwargs: Any):
        backend_kwargs.update(
            {
                "pos": view.position,
                "border_color": pyd_color_to_vispy(view.border_color),
                "border_width": view.border_width,
                "bgcolor": pyd_color_to_vispy(view.background_color),
                "padding": view.padding,
                "margin": view.margin,
            }
        )
        if view.size is not None:
            backend_kwargs["size"] = view.size

        self._native = scene.ViewBox(**backend_kwargs)

        # TODO: it would be nice if the responsibility of recursing through
        # the view tree was handled by the FrontEndFor logic...
        self._viz_set_scene(view.scene)
        self._viz_set_camera(view.camera)

    def _viz_set_camera(self, cam: core.Camera) -> None:
        if not cam.has_backend:
            cam._backend = Camera(cam)
        assert isinstance(cam.native, scene.cameras.BaseCamera)
        self._native.camera = cam.native
        cam.native.set_range(margin=0)  # TODO: put this elsewhere

    def _viz_set_scene(self, scene: core.Scene) -> None:
        if not scene.has_backend:
            scene._backend = Scene(scene)

        assert isinstance(scene.native, subscene.SubScene)
        self._native._scene = scene.native
        scene.native.parent = self._native

    def _viz_set_position(self, arg: tuple[float, float]) -> None:
        self._native.pos = arg

    def _viz_set_size(self, arg: tuple[float, float] | None) -> None:
        self._native.size = arg

    def _viz_set_background_color(self, arg: _types.Color | None) -> None:
        self._native.bgcolor = pyd_color_to_vispy(arg)

    def _viz_set_border_width(self, arg: float) -> None:
        self._native._border_width = arg
        self._native._update_line()
        self._native.update()

    def _viz_set_border_color(self, arg: _types.Color | None) -> None:
        self._native.border_color = pyd_color_to_vispy(arg)

    def _viz_set_padding(self, arg: int) -> None:
        self._native.padding = arg

    def _viz_set_margin(self, arg: int) -> None:
        self._native.margin = arg
