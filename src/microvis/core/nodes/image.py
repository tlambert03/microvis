from __future__ import annotations

from abc import abstractmethod
from typing import Any, Optional, Protocol, Tuple

from psygnal.containers import EventedObjectProxy
from pydantic import PrivateAttr

from ..._types import ArrayLike, ImageInterpolation
from .._base import Field, FrontEndFor
from .node import Node, NodeBackend


class Image(Node, FrontEndFor["ImageBackend"]):
    """A Image that can be placed in scene."""

    _data: ArrayLike = PrivateAttr()

    cmap: str = Field(default="grays", description="The colormap to use for the image.")
    clim: Optional[Tuple[float, float]] = Field(
        default=None,
        description="The contrast limits to use when rendering the image.",
    )
    gamma: float = Field(default=1.0, description="The gamma correction to use.")
    interpolation: ImageInterpolation = Field(
        default=ImageInterpolation.NEAREST, description="The interpolation to use."
    )

    def __init__(self, data: ArrayLike, **kwargs: Any) -> None:
        self.data = data
        super().__init__(**kwargs)

    @property
    def data(self) -> ArrayLike:
        return self._data

    @data.setter
    def data(self, data: ArrayLike) -> None:
        self._data = EventedObjectProxy(data)


# fmt: off
class ImageBackend(NodeBackend[Image], Protocol):
    """Protocol for a backend Image adapter object."""

    @abstractmethod
    def _viz_set_cmap(self, arg: str) -> None: ...
    @abstractmethod
    def _viz_set_clim(self, arg: Optional[Tuple[float, float]]) -> None: ...
    @abstractmethod
    def _viz_set_gamma(self, arg: float) -> None: ...
    @abstractmethod
    def _viz_set_interpolation(self, arg: ImageInterpolation) -> None: ...
    @abstractmethod
    def _viz_set_data(self, arg: ArrayLike) -> None: ...
# fmt: on
