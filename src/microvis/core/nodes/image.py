from __future__ import annotations

from abc import abstractmethod
from typing import Any, Iterable, Iterator, Protocol, Sequence, Union, cast, overload

import numpy as np
from pydantic import Field, validator

from cmap import LinearColormap
from microvis._types import ArrayLike, ImageInterpolation

from ._data import DataField, DataNode, DataNodeAdaptorProtocol


# fmt: off
class ImageBackend(DataNodeAdaptorProtocol['Image'], Protocol):
    """Protocol for a backend Image adaptor object."""

    @abstractmethod
    def _vis_set_cmap(self, arg: str) -> None: ...
    @abstractmethod
    def _vis_set_clim(self, arg: tuple[float, float] | None) -> None: ...
    @abstractmethod
    def _vis_set_gamma(self, arg: float) -> None: ...
    @abstractmethod
    def _vis_set_interpolation(self, arg: ImageInterpolation) -> None: ...
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

    def __iter__(self) -> Iterator[float]:  # type: ignore [override]
        yield self.min
        yield self.max

    @overload
    def __getitem__(self, index: int) -> float:
        ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[float]:
        ...

    def __getitem__(self, index: int | slice) -> float | Sequence[float]:
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

    def __iter__(self) -> Iterator[float]:  # type: ignore [override]
        yield self.pmin
        yield self.pmax

    @overload
    def __getitem__(self, index: int) -> float:
        ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[float]:
        ...

    def __getitem__(self, index: int | slice) -> float | Sequence[float]:
        return (self.pmin, self.pmax)[index]

    def __len__(self) -> int:
        return 2

    def apply(self, data: ArrayLike) -> tuple[float, float]:
        _min = data.min() if self.pmin == 0 else np.percentile(data, self.pmin)
        _max = data.max() if self.pmax == 100 else np.percentile(data, self.pmax)
        return (_min, _max)


class Image(DataNode[ImageBackend]):
    """A Image that can be placed in scene."""

    cmap: LinearColormap = Field(
        default=LinearColormap(colors=["black", "white"], id="gray"),
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
    def _vclim(cls, v: Any) -> dict | PercentileContrast | AbsContrast:
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
        """Return the current contrast limits, taking the data into account."""
        # TODO: from a typing perspective, having to cast to ArrayLike everytime
        # self._data is not None is a bit of an annoying hack.
        return (
            self.clim.apply(cast(ArrayLike, self.data_raw))
            if self._data is not None
            else (0, 0)
        )
