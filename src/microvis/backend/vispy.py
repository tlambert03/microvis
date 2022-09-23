from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast

from vispy import scene

from ._base import CanvasBase, ViewBase

if TYPE_CHECKING:
    import numpy as np

    from .._types import ValidClim, ValidCmap, ValidColor

ValidCamera = Literal["base", "panzoom", "perspective", "turntable", "fly", "arcball"]


class View(ViewBase, scene.Widget):
    def __init__(self) -> None:
        self._view2D_: scene.ViewBox | None = None
        self._view3D_: scene.ViewBox | None = None
        super().__init__()

    @property
    def _view2D(self) -> scene.ViewBox:
        if self._view2D_ is None:
            self._view2D_ = self.add_view()
            camera = scene.PanZoomCamera(aspect=1)
            camera.flip = (0, 1, 0)
            self._view2D_.camera = camera

        return self._view2D_

    @property
    def _view3D(self) -> scene.ViewBox:
        if self._view3D_ is None:
            self._view3D_ = self.add_view()
            self._view3D_.camera = scene.ArcballCamera()
        return self._view3D_

    def _reset_camera(
        self,
        *,
        dim: int = 2,
        x: tuple | None = None,
        y: tuple | None = None,
        z: tuple | None = None,
        margin: float = 0.0,
    ) -> None:
        if dim == 2:
            cam = self._view2D.camera
        elif dim == 3:
            cam = self._view3D.camera
        else:
            raise ValueError(f"Invalid dimension: {dim}")
        cam.reset()
        cam.set_range(x=x, y=y, z=z, margin=margin)

    def _do_add_image(
        self,
        data: Any,
        cmap: ValidCmap | None = None,
        clim: ValidClim = "auto",
        **kwargs: Any,
    ) -> scene.visuals.Image:
        cmap = cmap or "grays"
        if data.ndim == 2:
            image = scene.Image(data, cmap=cmap, clim=clim, **kwargs)
            self._view2D.add(image)
            self._reset_camera()  # FIXME: backends shoulnd't handle this
        elif data.ndim == 3:
            image = scene.Volume(data, cmap=cmap, clim=clim, **kwargs)
            self._view3D.add(image)
            self._reset_camera(dim=3)  # FIXME: backends shoulnd't handle this
        else:
            raise NotImplementedError(f"Unsupported data dimension: {data.ndim}")
        return image


class Canvas(CanvasBase):
    def __init__(
        self,
        background_color: str | None = None,
        size: tuple[int, int] = (600, 600),
        **backend_kwargs: Any,
    ) -> None:
        backend_kwargs.setdefault("keys", "interactive")
        self._native = scene.SceneCanvas(
            bgcolor=background_color, size=size, **backend_kwargs
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

        row, col = next(
            (val[:2] for val in self._grid._grid_widgets.values() if val[-1] is item),
            (None, None),
        )

        self._grid.remove_widget(item)
        del self._grid._cells[row][col]
        item.parent = None

        # fixup next_cell if this was the last item
        # FIXME: take column_span into account
        if col and col == self._grid._next_cell[1] - 1:
            self._grid._next_cell[1] -= 1
        if row and row == self._grid._next_cell[0] - 1:
            self._grid._next_cell[0] -= 1

        self._grid.update()

    def show(self) -> None:
        """Show canvas."""
        self.native.show()

    def close(self) -> None:
        """Close canvas."""
        self.native.close()

    def render(
        self,
        region: tuple[int, int, int, int] | None = None,
        size: tuple[int, int] | None = None,
        bgcolor: ValidColor = None,
        crop: np.ndarray | tuple[int, int, int, int] | None = None,
        alpha: bool = True,
    ) -> np.ndarray:
        """Render to screenshot."""
        data = self.native.render(
            region=region, size=size, bgcolor=bgcolor, crop=crop, alpha=alpha
        )
        return cast("np.ndarray", data)

    def __enter__(self) -> Canvas:
        super().__enter__()
        self.native._backend._vispy_warmup()
        return self

    def __exit__(self, *a: Any) -> None:
        self.native.__exit__(*a)
        super().__exit__()
