from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vispy import scene

from ... import core
from ._node import Node

if TYPE_CHECKING:
    from ..._types import ArrayLike, ImageInterpolation


class Image(Node):
    """Vispy backend adaptor for an Image node."""

    _native: scene.Image

    def __init__(self, image: core.Image, **backend_kwargs: Any) -> None:

        backend_kwargs.setdefault("texture_format", "auto")
        backend_kwargs.update(
            {
                "cmap": str(image.cmap),
                "clim": image.clim_applied(),
                "gamma": image.gamma,
                "interpolation": image.interpolation.value,
            }
        )
        self._native = scene.Image(image.data, **backend_kwargs)

    def _viz_set_cmap(self, arg: str) -> None:
        self._native.cmap = str(arg)

    def _viz_set_clim(self, arg: tuple[float, float] | None) -> None:
        self._native.clim = arg

    def _viz_set_gamma(self, arg: float) -> None:
        self._native.gamma = arg

    def _viz_set_interpolation(self, arg: ImageInterpolation) -> None:
        self._native.interpolation = arg.value

    def _viz_set_data(self, arg: ArrayLike) -> None:
        self._native.set_data(arg)
