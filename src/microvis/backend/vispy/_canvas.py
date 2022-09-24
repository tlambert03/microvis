from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import numpy as np
from vispy import scene

from microvis import _protocols, _util

if TYPE_CHECKING:
    from microvis import _types
    from microvis.core import Canvas, View


class Canvas(_protocols.CanvasBackend):
    """Canvas interface for Vispy Backend."""

    def __init__(self, canvas: Canvas, **backend_kwargs: Any) -> None:
        backend_kwargs.setdefault("keys", "interactive")
        self._native = scene.SceneCanvas(
            size=canvas.size,
            title=canvas.title,
            show=canvas.visible,
            bgcolor=_util.color_to_np(canvas.background_color),
            **backend_kwargs,
        )

    def _viz_get_native(self) -> scene.SceneCanvas:
        return self._native

    def _viz_add_view(self, view: View) -> None:
        # view.native = cast(scene.ViewBox, view.native)
        self._native.central_widget.add_widget(view.native)

    def _viz_set_width(self, arg: int) -> None:
        _height = self._native.size[1]
        self._native.size = (arg, _height)

    def _viz_set_height(self, arg: int) -> None:
        _width = self._native.size[0]
        self._native.size = (_width, arg)

    def _viz_set_background_color(self, arg: _types.Color | None) -> None:
        self._native.bgcolor = _util.color_to_np(arg)

    def _viz_set_visible(self, arg: bool) -> None:
        self._native.show(visible=arg)

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

    # def __getitem__(self, idxs: tuple[int, int]) -> View:
    #     return cast(View, self._grid.__getitem__(idxs))

    # def __delitem__(self, idxs: tuple[int, int]) -> None:
    #     item = self._grid[idxs]

    #     row, col = next(
    #         (val[:2] for val in self._grid._grid_widgets.values() if val[-1] is item),
    #         (None, None),
    #     )

    #     self._grid.remove_widget(item)
    #     del self._grid._cells[row][col]
    #     item.parent = None

    #     # fixup next_cell if this was the last item
    #     # FIXME: take column_span into account
    #     if col and col == self._grid._next_cell[1] - 1:
    #         self._grid._next_cell[1] -= 1
    #     if row and row == self._grid._next_cell[0] - 1:
    #         self._grid._next_cell[0] -= 1

    #     self._grid.update()
