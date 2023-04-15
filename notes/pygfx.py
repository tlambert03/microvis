from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast

import pygfx
from wgpu.gui.auto import WgpuCanvas

from ._base import CanvasBase, ViewBase

if TYPE_CHECKING:
    import numpy as np
    from wgpu.gui.base import WgpuAutoGui, WgpuCanvasBase

    from microvis._types import ValidClim, ValidCmap, ValidColor

    class PygfxCanvas(WgpuAutoGui, WgpuCanvasBase):
        ...


ValidCamera = Literal["base", "panzoom", "perspective", "turntable", "fly", "arcball"]


class View(ViewBase):
    def __init__(self) -> None:
        self._scene2D_: pygfx.Scene | None = None
        self._scene3D_: pygfx.Scene | None = None
        super().__init__()

    def _visit(self, viewport: pygfx.Viewport) -> None:
        viewport.render(self._scene2D, self._camera2)
        self._controller2.update_camera(self._camera2)

    @property
    def camera(self) -> pygfx.Camera:
        return self._camera2

    @property
    def _scene2D(self) -> pygfx.Scene:
        if self._scene2D_ is None:
            self._scene2D_ = pygfx.Scene()
            camera = pygfx.OrthographicCamera(512, 512)
            camera.position.set(256, 256, 0)
            camera.scale.y = -1
            self._camera2 = camera
            self._controller2 = pygfx.PanZoomController(camera.position.clone())
        return self._scene2D_

    @property
    def _view3D(self) -> pygfx.Scene:
        if self._scene3D_ is None:
            self._scene3D_ = pygfx.Scene()
            self._camera3 = pygfx.PerspectiveCamera()
            self._controller3 = pygfx.OrbitOrthoController()

        return self._scene3D_

    def _do_add_image(
        self,
        data: Any,
        cmap: ValidCmap | None = None,
        clim: ValidClim = "auto",
        **kwargs: Any,
    ) -> pygfx.Image:
        tex = pygfx.Texture(data, dim=2)
        image = pygfx.Image(
            pygfx.Geometry(grid=tex),
            pygfx.ImageBasicMaterial(clim=(0, 255), map=cmap),
        )
        # image.position.x = 0

        # image = pygfx.Mesh(
        #     pygfx.plane_geometry(512, 512),
        #     pygfx.MeshBasicMaterial(map=tex.get_view(filter="linear")),
        # )

        self._scene2D.add(image)
        return image


class Canvas(CanvasBase):
    def __init__(
        self,
        background_color: str | None = None,
        size: tuple[int, int] = (600, 600),
        **backend_kwargs: Any,
    ) -> None:
        # note... on qt, this shows by default
        self._canvas: PygfxCanvas = WgpuCanvas(size=size, **backend_kwargs)
        if hasattr(self._canvas, "hide"):
            self._canvas.hide()

        self._renderer = pygfx.renderers.WgpuRenderer(self._canvas)
        self._viewport: pygfx.Viewport = pygfx.Viewport(self._renderer)
        self._grid: dict[tuple[int, int], View] = {}

    @property
    def native(self) -> pygfx.renderers.WgpuRenderer:
        # choosing renderer over canvas because it also has a pointer to the canvas
        return self._renderer

    def __getitem__(self, idxs: tuple[int, int]) -> View:
        #  w, h = self._canvas.get_logical_size()
        if idxs not in self._grid:
            view = View()
            _ = view._scene2D  # FIXME: temp
            view._controller2.add_default_event_handlers(self._viewport, view._camera2)
            self._grid[idxs] = view
        return self._grid[idxs]

    def __delitem__(self, idxs: tuple[int, int]) -> None:
        # todo
        ...

    def show(self) -> None:
        """Show canvas."""
        if hasattr(self._canvas, "show"):
            self._canvas.show()
        self._canvas.request_draw(self._animate)

    def _animate(self, viewport: pygfx.Viewport | None = None) -> None:
        vp = viewport or self._viewport
        for scene in self._grid.values():
            scene._visit(vp)
        if hasattr(vp.renderer, "flush"):
            vp.renderer.flush()
        if viewport is None:
            self._canvas.request_draw()

    def close(self) -> None:
        """Close canvas."""
        self._canvas.close()

    def render(
        self,
        region: tuple[int, int, int, int] | None = None,
        size: tuple[int, int] | None = None,
        bgcolor: ValidColor = None,
        crop: np.ndarray | tuple[int, int, int, int] | None = None,
        alpha: bool = True,
    ) -> np.ndarray:
        """Render to screenshot."""
        # Create offscreen canvas, renderer and scene
        from wgpu.gui.offscreen import WgpuCanvas

        w, h = self._canvas.get_logical_size()
        canvas = WgpuCanvas(width=w, height=h, pixel_ratio=1)
        renderer = pygfx.renderers.WgpuRenderer(canvas)
        viewport = pygfx.Viewport(renderer)
        canvas.request_draw(lambda: self._animate(viewport))
        return cast("np.ndarray", canvas.draw())
