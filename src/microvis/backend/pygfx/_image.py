from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygfx

from microvis import core

from ._node import Node

if TYPE_CHECKING:
    from microvis._types import ArrayLike, ImageInterpolation


class Image(Node):
    """pygfx backend adaptor for an Image node."""

    _native: pygfx.Image
    _material: pygfx.ImageBasicMaterial

    def __init__(self, image: core.Image, **backend_kwargs: Any) -> None:
        if (data := image.data_raw) is not None:
            dim = data.ndim
            if dim > 2 and data.shape[-1] <= 4:
                dim -= 1  # last array dim is probably (a subset of) rgba
        else:
            dim = 2
        # TODO: unclear whether get_view() is better here...
        self._texture = pygfx.Texture(data, dim=dim).get_view()
        self._geometry = pygfx.Geometry(grid=self._texture)
        self._material = pygfx.ImageBasicMaterial(
            clim=image.clim_applied(),
            # map=str(image.cmap), # TODO: map needs to be a TextureView
        )
        # TODO: gamma?
        # TODO: interpolation?
        self._native = pygfx.Image(self._geometry, self._material)

    def _vis_set_cmap(self, arg: str) -> None:
        self._material.map = arg

    def _vis_set_clim(self, arg: tuple[float, float] | None) -> None:
        self._material.clim = arg

    def _vis_set_gamma(self, arg: float) -> None:
        raise NotImplementedError

    def _vis_set_interpolation(self, arg: ImageInterpolation) -> None:
        raise NotImplementedError

    def _vis_set_data(self, arg: ArrayLike) -> None:
        raise NotImplementedError