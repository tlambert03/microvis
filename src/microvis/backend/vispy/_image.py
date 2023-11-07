from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vispy import scene

from ._node import Node

if TYPE_CHECKING:
    from microvis import core
    from microvis._types import ArrayLike, ImageInterpolation


class Image(Node):
    """Vispy backend adaptor for an Image node."""

    _vispy_node: scene.Image

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
        self._vispy_node = scene.Image(image.data, **backend_kwargs)

    def _vis_set_cmap(self, arg: str) -> None:
        self._vispy_node.cmap = str(arg)

    def _vis_set_clim(self, arg: tuple[float, float] | None) -> None:
        self._vispy_node.clim = arg

    def _vis_set_gamma(self, arg: float) -> None:
        self._vispy_node.gamma = arg

    def _vis_set_interpolation(self, arg: ImageInterpolation) -> None:
        self._vispy_node.interpolation = arg.value

    def _vis_set_data(self, arg: ArrayLike) -> None:
        self._vispy_node.set_data(arg)
