from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import Any, Iterable, Optional, Protocol, Sequence, Tuple, Union

import numpy as np
from pydantic import Field, validator

from ..._types import ArrayLike, ImageInterpolation
from .._base import Field
from ._data import DataField, DataNode, DataNodeBackend


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


class AbsContrast(DataField, Sequence[float]):
    """Contrast limits in absolute units of the data."""

    min: float = Field(0, description="Minimum contrast value.")
    max: float

    def __init__(self, max_or_range: float | Iterable[float], min: float = 0) -> None:
        if isinstance(max_or_range, (float, int)):
            _max = max_or_range
            _min = min
        elif isinstance(max_or_range, Iterable):
            _min, _max = max_or_range
        else:
            raise TypeError("First argument must be a number or an iterable.")
        super().__init__(min=_min, max=_max)

    def __iter__(self) -> Iterable[float]:  # type: ignore
        yield self.min
        yield self.max

    def __getitem__(self, index: int | slice) -> float:
        return (self.min, self.max)[index]

    def __len__(self) -> int:
        return 2


class PercentileContrast(DataField, Sequence[float]):
    """Percentile contrast limits."""

    pmin: float = Field(
        default=0, ge=0, le=100, description="Minimum contrast percentile."
    )
    pmax: float = Field(
        default=100, ge=0, le=100, description="Maximum contrast percentile."
    )

    def __iter__(self) -> Iterable[float]:  # type: ignore
        yield self.pmin
        yield self.pmax

    def __getitem__(self, index: int | slice) -> float:
        return (self.pmin, self.pmax)[index]

    def __len__(self) -> int:
        return 2

    def apply(self, data: ArrayLike) -> tuple[float, float]:
        _min = data.min() if self.pmin == 0 else np.percentile(data, self.pmin)
        _max = data.max() if self.pmax == 100 else np.percentile(data, self.pmax)
        return (_min, _max)


class Cmap(str, Enum):
    GRAYS = "grays"
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    GREEN = "green"
    BLUE = "blue"
    RED = "red"
    CYAN = "cyan"
    MAGENTA = "magenta"
    YELLOW = "yellow"
    ORANGE = "orange"
    PURPLE = "purple"
    BONE = "bone"
    PINK = "pink"
    HOT = "hot"

    def __str__(self) -> str:
        return self.value


class Image(DataNode[ImageBackend]):
    """A Image that can be placed in scene."""

    cmap: Cmap = Field(
        default="grays",
        description="The colormap to use for the image.",
    )
    clim: Union[AbsContrast, PercentileContrast] = Field(
        default_factory=PercentileContrast,
        description="The contrast limits to use when rendering the image.",
    )
    gamma: float = Field(default=1.0, description="The gamma correction to use.")
    interpolation: ImageInterpolation = Field(
        default=ImageInterpolation.NEAREST,
        description="The interpolation to use.",
    )

    @validator("clim", pre=True)
    def _vclim(cls, v: Any) -> Union[dict, PercentileContrast, AbsContrast]:
        # contrast limits can be expressed Falsey (autoscale 0-100%)
        # a tuple (min, max) or scalar (max) of Absolute contrast
        # a dict {'min', 'max'} or {'pmin', 'pmax'}
        if isinstance(v, (dict, PercentileContrast, AbsContrast)):
            return v
        if v in (None, {}, (), False):
            return PercentileContrast()
        if isinstance(v, (tuple, list, int, float)):
            return AbsContrast(v)
        raise TypeError("clim must be an iterable or dict.")

    def clim_applied(self) -> tuple[float, float]:
        return self.clim.apply(self.data_raw) if self._data is not None else (0, 0)
