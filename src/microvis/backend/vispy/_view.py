from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vispy import scene

from microvis import _protocols, _util

if TYPE_CHECKING:
    from microvis import _types, core


class View(_protocols.ViewBackend):
    """View interface for Vispy Backend."""

    def __init__(self, view: core.View, **backend_kwargs: Any):
        backend_kwargs.update(
            {
                "pos": view.position,
                "border_color": _util.color_to_np(view.border_color),
                "border_width": view.border_width,
                "bgcolor": _util.color_to_np(view.background_color),
                "padding": view.padding,
                "margin": view.margin,
            }
        )
        if view.size is not None:
            backend_kwargs["size"] = view.size

        self._viewbox = scene.ViewBox(**backend_kwargs)

    def _viz_get_native(self) -> scene.ViewBox:
        return self._viewbox

    def _viz_set_camera(self, arg: core.Camera) -> None:
        raise NotImplementedError()

    def _viz_set_scene(self, arg: core.Scene) -> None:
        raise NotImplementedError()

    def _viz_set_position(self, arg: tuple[float, float]) -> None:
        self._viewbox.pos = arg

    def _viz_set_size(self, arg: tuple[float, float] | None) -> None:
        self._viewbox.size = arg

    def _viz_set_background_color(self, arg: _types.Color | None) -> None:
        self._viewbox.bgcolor = _util.color_to_np(arg)

    def _viz_set_border_width(self, arg: float) -> None:
        self._viewbox._border_width = arg
        self._viewbox._update_line()
        self._viewbox.update()

    def _viz_set_border_color(self, arg: _types.Color | None) -> None:
        self._viewbox.border_color = _util.color_to_np(arg)

    def _viz_set_padding(self, arg: int) -> None:
        self._viewbox.padding = arg

    def _viz_set_margin(self, arg: int) -> None:
        self._viewbox.margin = arg

    def _viz_set_visible(self, arg: bool) -> None:
        self._viewbox.visible = arg
