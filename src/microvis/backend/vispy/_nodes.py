from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vispy import scene

from microvis import _protocols

from ._view import _SupportsVisibility

if TYPE_CHECKING:
    import numpy as np
    from microvis import core


class Image(_SupportsVisibility, _protocols.ImageBackend):
    _native: scene.Image

    def __init__(self, data: core.Image, **backend_kwargs: Any):
        self._native = scene.Image(data.data, **backend_kwargs)

    def _viz_set_data(self, arg: np.ndarray) -> None:
        self._native.data = arg
