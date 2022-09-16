from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast

from vispy import scene
from ._base import CanvasBase, ViewBase

if TYPE_CHECKING:
    from .._types import ValidClim, ValidCmap


ValidCamera = Literal["base", "panzoom", "perspective", "turntable", "fly", "arcball"]


class View(ViewBase, scene.Widget):
    _view: scene.ViewBox

    def __init__(self) -> None:
        self._view2D_: scene.ViewBox | None = None
        super().__init__()

    @property
    def _view2D(self) -> scene.ViewBox:
        if self._view2D_ is None:
            self._view2D_ = self.add_view()
            self._view2D_.camera = scene.PanZoomCamera(aspect=1)
        return self._view2D_

    def _reset_view(
        self,
        *,
        dim: int = 2,
        x: tuple | None = None,
        y: tuple | None = None,
        z: tuple | None = None,
        margin: float = 0.0,
    ) -> None:
        if dim == 2:
            self._view2D.camera.reset()
            self._view2D.camera.set_range(x=x, y=y, z=z, margin=margin)
        else:
            raise ValueError(f"Invalid dimension: {dim}")

    def add_image(
        self,
        data: Any,
        cmap: ValidCmap = "gray",
        clim: ValidClim = "auto",
        **kwargs: Any,
    ) -> scene.visuals.Image:
        image = scene.Image(data, cmap=cmap, clim=clim, **kwargs)
        self._view2D.add(image)
        self._reset_view()
        return image


class Canvas(CanvasBase):
    def __init__(
        self,
        background_color: str | None = None,
        size: tuple[int, int] = (600, 600),
        show: bool = False,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("keys", "interactive")
        self._native = scene.SceneCanvas(
            bgcolor=background_color, size=size, show=show, **kwargs
        )
        self._grid = self._native.central_widget.add_grid()
        self._grid._default_class = View

    @property
    def native(self) -> scene.SceneCanvas:
        return self._native

    def __getitem__(self, idxs: tuple[int, int]) -> View:
        return cast(View, self._grid.__getitem__(idxs))

    def __delitem__(self, idxs: tuple[int, int]) -> None:
        item = self._grid[idxs]

        row, col = (None, None)
        for val in self._grid._grid_widgets.values():
            if val[-1] is item:
                row, col = val[:2]
                break

        self._grid.remove_widget(item)
        item.parent = None
        del self._grid._cells[row][col]

        # fixup next_cell if this was the last item
        # FIXME: take column_span into account
        if col and col == self._grid._next_cell[1] - 1:
            self._grid._next_cell[1] -= 1
        if row and row == self._grid._next_cell[0] - 1:
            self._grid._next_cell[0] -= 1

        self._grid.update()

    def show(self) -> None:
        self.native.show()
