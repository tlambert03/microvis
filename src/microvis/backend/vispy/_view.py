from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vispy import scene

from microvis import _protocols

from ._util import pyd_color_to_vispy

if TYPE_CHECKING:
    from vispy.scene import Node
    from vispy.scene.cameras import BaseCamera
    from vispy.scene.subscene import SubScene

    from microvis import _types, core


class _SupportsNative:
    _native: Any

    def __init__(self, native: Any) -> None:
        self._native = native

    def _viz_get_native(self) -> Any:
        return self._native


class _SupportsVisibility(_SupportsNative):
    _native: Node

    def _viz_set_visible(self, arg: bool) -> None:
        self._native.visible = arg


class Scene(_SupportsVisibility, _protocols.NodeBackend):
    _native: SubScene

    def _viz_add_node(self, node: core.Node) -> None:
        node.native.parent = self._native


class Camera(_SupportsVisibility, _protocols.CameraBackend):
    _native: BaseCamera

    def _viz_add_node(self, node: core.Node) -> None:
        raise NotImplementedError

    def _viz_set_interactive(self, arg: bool) -> None:
        raise NotImplementedError()

    def _viz_set_zoom(self, arg: float) -> None:
        raise NotImplementedError()

    def _viz_set_center(self, arg: tuple[float, ...]) -> None:
        raise NotImplementedError()

    def _viz_set_type(self, arg: _types.CameraType) -> None:
        assert isinstance(self._native.parent, scene.ViewBox)
        self._native.parent.camera = str(arg)

    def _viz_reset(self) -> None:
        self._native.set_range(margin=0)


class View(_SupportsVisibility, _protocols.ViewBackend):
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

        camera = str(view.camera.type)
        self._native = scene.ViewBox(camera=camera, **backend_kwargs)

    def _viz_set_camera(self, arg: core.Camera) -> None:
        raise NotImplementedError()

    def _viz_set_scene(self, arg: core.Scene) -> None:
        raise NotImplementedError()

    def _viz_get_scene(self) -> _protocols.NodeBackend:
        return Scene(self._native.scene)

    def _viz_get_camera(self) -> _protocols.CameraBackend:
        return Camera(self._native.camera)

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
