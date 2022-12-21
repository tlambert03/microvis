from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, Union, cast

import pygfx

from microvis import core

from ._view import View as ViewAdaptor

if TYPE_CHECKING:

    import numpy as np
    from qtpy.QtWidgets import QApplication
    from typing_extensions import TypeAlias, TypeGuard
    from wgpu.gui import glfw, jupyter, offscreen, qt

    from microvis import _types

    # from wgpu.gui.auto import WgpuCanvas
    # ... will result in one of the following canvas classes
    TypeWgpuCanvasType: TypeAlias = Union[
        type[offscreen.WgpuCanvas],  # if WGPU_FORCE_OFFSCREEN=1
        type[jupyter.WgpuCanvas],  # if is_jupyter()
        type[glfw.WgpuCanvas],  # if glfw is installed
        type[qt.WgpuCanvas],  # if any pyqt backend is installed
    ]
    # TODO: lol... there's probably a better way to do this :)
    WgpuCanvasType: TypeAlias = Union[
        offscreen.WgpuCanvas,  # if WGPU_FORCE_OFFSCREEN=1
        jupyter.WgpuCanvas,  # if is_jupyter()
        glfw.WgpuCanvas,  # if glfw is installed
        qt.WgpuCanvas,  # if any pyqt backend is installed
    ]


# FIXME: move
_app: QApplication | None = None


def _start_qt() -> Any:
    import sys

    from qtpy.QtWidgets import QApplication

    global _app
    if not QApplication.instance():
        _app = QApplication(sys.argv)


def _is_qt_canvas_type(obj: type) -> TypeGuard[type[qt.WgpuCanvas]]:
    if wgpu_qt := sys.modules.get("wgpu.gui.qt"):
        return issubclass(obj, wgpu_qt.WgpuCanvas)
    return False


class Canvas(core.canvas.CanvasBackend):
    """Canvas interface for pygfx Backend."""

    def __init__(self, canvas: core.Canvas, **backend_kwargs: Any) -> None:
        # wgpu.gui.auto.WgpuCanvas is a "magic" import that itself is context sensitive
        # see TYPE_CHECKING section above for details
        from wgpu.gui.auto import WgpuCanvas

        WgpuCanvas = cast("TypeWgpuCanvasType", WgpuCanvas)
        # TODO: we might decide to have "chosen" the scope prior to this point
        # but for now, as long as we use wgpu.gui.auto, it *may* return the Qt
        # canvas, which requires a QApplication to be instantiated beforehand.
        # This little bit of QApplication magic might move in the future.
        if _is_qt_canvas_type(WgpuCanvas):
            _start_qt()

        canvas = WgpuCanvas(size=canvas.size, title=canvas.title, **backend_kwargs)
        self._wgpu_canvas = cast("WgpuCanvasType", canvas)
        # TODO: background_color
        # the qt backend, this shows by default...
        # if we need to prevent it, we could potentially monkeypatch during init.
        if hasattr(self._wgpu_canvas, "hide"):
            self._wgpu_canvas.hide()

        self._renderer = pygfx.renderers.WgpuRenderer(self._wgpu_canvas)
        self._viewport: pygfx.Viewport = pygfx.Viewport(self._renderer)
        self._views: list[ViewAdaptor] = []
        # self._grid: dict[tuple[int, int], View] = {}

    def _viz_get_native(self) -> WgpuCanvasType:
        return self._wgpu_canvas

    def _viz_set_visible(self, arg: bool) -> None:
        if hasattr(self._wgpu_canvas, "show"):
            self._wgpu_canvas.show()
        self._wgpu_canvas.request_draw(self._animate)

    def _animate(self, viewport: pygfx.Viewport | None = None) -> None:
        vp = viewport or self._viewport
        for view in self._views:
            view._visit(vp)
        if hasattr(vp.renderer, "flush"):
            vp.renderer.flush()
        if viewport is None:
            self._wgpu_canvas.request_draw()

    def _viz_add_view(self, view: core.View) -> None:
        adaptor: ViewAdaptor = view.backend_adaptor()
        adaptor._camera.set_viewport(self._viewport)
        self._views.append(adaptor)

    def _viz_set_width(self, arg: int) -> None:
        _, height = self._wgpu_canvas.get_logical_size()
        self._wgpu_canvas.set_logical_size(arg, height)

    def _viz_set_height(self, arg: int) -> None:
        width, _ = self._wgpu_canvas.get_logical_size()
        self._wgpu_canvas.set_logical_size(width, arg)

    def _viz_set_size(self, arg: tuple[int, int]) -> None:
        self._wgpu_canvas.set_logical_size(*arg)

    def _viz_set_background_color(self, arg: _types.Color | None) -> None:
        raise NotImplementedError()

    def _viz_set_title(self, arg: str) -> None:
        raise NotImplementedError()

    def _viz_close(self) -> None:
        """Close canvas."""
        self._wgpu_canvas.close()

    def _viz_render(
        self,
        region: tuple[int, int, int, int] | None = None,
        size: tuple[int, int] | None = None,
        bgcolor: _types.ValidColor = None,
        crop: np.ndarray | tuple[int, int, int, int] | None = None,
        alpha: bool = True,
    ) -> np.ndarray:
        """Render to screenshot."""
        from wgpu.gui.offscreen import WgpuCanvas

        w, h = self._wgpu_canvas.get_logical_size()
        canvas = WgpuCanvas(width=w, height=h, pixel_ratio=1)
        renderer = pygfx.renderers.WgpuRenderer(canvas)
        viewport = pygfx.Viewport(renderer)
        canvas.request_draw(lambda: self._animate(viewport))
        return cast("np.ndarray", canvas.draw())
