from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import numpy as np
from vispy import scene

from microvis import core

from ._util import pyd_color_to_vispy

if TYPE_CHECKING:
    from microvis import _types


class Canvas(core.canvas.CanvasBackend):
    """Canvas interface for Vispy Backend."""

    def __init__(self, canvas: core.Canvas, **backend_kwargs: Any) -> None:
        backend_kwargs.setdefault("keys", "interactive")
        self._native = scene.SceneCanvas(
            size=canvas.size,
            title=canvas.title,
            show=canvas.visible,
            bgcolor=pyd_color_to_vispy(canvas.background_color),
            **backend_kwargs,
        )

    def _viz_get_native(self) -> scene.SceneCanvas:
        return self._native

    def _viz_set_visible(self, arg: bool) -> None:
        self._native.show(visible=arg)

    def _viz_add_view(self, view: core.View) -> None:
        if not isinstance(view.native, scene.ViewBox):
            raise TypeError("View must be a Vispy ViewBox")
        self._native.central_widget.add_widget(view.native)

    def _viz_set_width(self, arg: int) -> None:
        _height = self._native.size[1]
        self._native.size = (arg, _height)

    def _viz_set_height(self, arg: int) -> None:
        _width = self._native.size[0]
        self._native.size = (_width, arg)

    def _viz_set_size(self, arg: tuple[int, int]) -> None:
        self._native.size = arg

    def _viz_set_background_color(self, arg: _types.Color | None) -> None:
        self._native.bgcolor = pyd_color_to_vispy(arg)

    def _viz_set_title(self, arg: str) -> None:
        self._native.title = arg

    def _viz_close(self) -> None:
        """Close canvas."""
        self._native.close()

    def _viz_render(
        self,
        region: tuple[int, int, int, int] | None = None,
        size: tuple[int, int] | None = None,
        bgcolor: _types.ValidColor = None,
        crop: np.ndarray | tuple[int, int, int, int] | None = None,
        alpha: bool = True,
    ) -> np.ndarray:
        """Render to screenshot."""
        data = self._native.render(
            region=region, size=size, bgcolor=bgcolor, crop=crop, alpha=alpha
        )
        return cast("np.ndarray", data)

    def _viz_get_ipython_mimebundle(
        self, *args: Any, **kwargs: Any
    ) -> dict | tuple[dict, dict]:
        return self._native._repr_mimebundle_(*args, **kwargs)
