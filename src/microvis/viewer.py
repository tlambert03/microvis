from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any


from . import _validators as valid
from . import backend as _backend
from .util import in_notebook

if TYPE_CHECKING:
    from vispy.color import Color
    from .backend._base import CanvasBase, Image, ViewBase
    from ._types import ValidClim, ValidCmap


@dataclass
class CanvasAttrs:
    background_color: str | Color | None = None
    size: tuple[int, int] = (800, 600)
    title: str = ""
    screen_position: tuple[int, int] | None = None
    resizable: bool = True


class Viewer:
    def __init__(
        self,
        background_color: str | None = None,
        size: tuple[int, int] = (600, 600),
        show: bool = False,
        backend: str = "vispy",
    ) -> None:
        backend_module = getattr(_backend, backend)
        Canvas: type[CanvasBase] = backend_module.Canvas
        if background_color is None:
            background_color = "white" if in_notebook() else "black"
        self.canvas = Canvas(background_color=background_color, size=size, show=show)

    def add_image(
        self,
        data: Any,
        cmap: ValidCmap = "gray",
        clim: ValidClim = "auto",
        idx: tuple[int, int] = (0, 0),
        **kwargs: Any,
    ) -> Image:
        clim = valid.clim(clim)
        cmap = valid.cmap(cmap)
        return self[idx].add_image(data, cmap=cmap, clim=clim, **kwargs)

    def show(self) -> None:
        self.canvas.show()

    def _repr_mimebundle_(self, *_: Any, **__: Any) -> Any:
        if method := getattr(self.canvas.native, "_repr_mimebundle_"):
            return method()
        raise NotImplementedError()

    def __getitem__(self, idx: tuple[int, int]) -> ViewBase:
        return self.canvas[idx]

    def __delitem__(self, idxs: tuple[int, int]) -> None:
        del self.canvas[idxs]

    def __enter__(self) -> Viewer:
        self.canvas.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        self.canvas.__exit__(*args)


# Viewer
#   - Canvas
#     - 1 or more View ([m, n] with [0, 0] as default)
#       - add_<layer>()

# Application ... some sort of event loop
