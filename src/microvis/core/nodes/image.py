from __future__ import annotations

from abc import abstractmethod
from typing import ClassVar, Optional, Protocol, Tuple

from ..._types import ImageInterpolation
from .._base import Field, FrontEndFor
from ._data import DataNode, DataNodeBackend


# fmt: off
class ImageBackend(DataNodeBackend['Image'], Protocol):
    """Protocol for a backend Image adapter object."""

    @abstractmethod
    def _viz_set_cmap(self, arg: str) -> None: ...
    @abstractmethod
    def _viz_set_clim(self, arg: Optional[Tuple[float, float]]) -> None: ...
    @abstractmethod
    def _viz_set_gamma(self, arg: float) -> None: ...
    @abstractmethod
    def _viz_set_interpolation(self, arg: ImageInterpolation) -> None: ...
# fmt: on


class Image(DataNode, FrontEndFor[ImageBackend]):
    """A Image that can be placed in scene."""

    _BackendProtocol: ClassVar[type] = ImageBackend

    cmap: str = Field(default="grays", description="The colormap to use for the image.")
    clim: Optional[Tuple[float, float]] = Field(
        default=None,
        description="The contrast limits to use when rendering the image.",
    )
    gamma: float = Field(default=1.0, description="The gamma correction to use.")
    interpolation: ImageInterpolation = Field(
        default=ImageInterpolation.NEAREST, description="The interpolation to use."
    )