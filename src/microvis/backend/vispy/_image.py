from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vispy import scene

from microvis import core

from ._node import Node

if TYPE_CHECKING:
    from microvis._types import ArrayLike, ImageInterpolation


class Image(Node):
    """Vispy backend adaptor for an Image node."""

    _vispy_image: scene.Image

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
        self._vispy_image = scene.Image(image.data, **backend_kwargs)

    def _viz_set_cmap(self, arg: str) -> None:
        self._vispy_image.cmap = str(arg)

    def _viz_set_clim(self, arg: tuple[float, float] | None) -> None:
        self._vispy_image.clim = arg

    def _viz_set_gamma(self, arg: float) -> None:
        self._vispy_image.gamma = arg

    def _viz_set_interpolation(self, arg: ImageInterpolation) -> None:
        self._vispy_image.interpolation = arg.value

    def _viz_set_data(self, arg: ArrayLike) -> None:
        self._vispy_image.set_data(arg)
