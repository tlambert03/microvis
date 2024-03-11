"""Models defining slicing of data.

FIXME: none of this is hooked up anywhere yet.
"""

from __future__ import annotations

from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Optional,
    Sequence,
    SupportsIndex,
    Union,
)

from psygnal import EventedModel
from pydantic import validator

from ._vis_model import Field


class Slice(EventedModel):
    start: Optional[float] = Field(default=None)
    stop: Optional[float] = Field(default=None)
    step: Optional[float] = Field(default=None)

    def __init__(_model_self_, *args: float, **data: float) -> None:
        if args:
            if data:
                raise TypeError("Cannot pass both args and kwargs")
            _slc = slice(*args)
            data = {"start": _slc.start, "stop": _slc.stop, "step": _slc.step}
        super().__init__(**data)

    def indices(self, len: SupportsIndex) -> tuple[int, int, int]:
        """Return (start, stop, step) tuple representing indices.

        Assuming a sequence of length `len`, calculate the start and stop indices, and
        the stride length of the extended slice described by S. Out of bounds indices
        are clipped in a manner consistent with the handling of normal slices.

        It returns a tuple of three integers; respectively these are the
        start and stop indices and the step or stride length of the slice.
        """
        return slice(self.start, self.stop, self.step).indices(len)

    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> Slice:
        if v is None:
            return cls()
        if isinstance(v, slice):
            return cls(start=v.start, stop=v.stop, step=v.step)
        if isinstance(v, (int, float)):
            return cls(v)
        raise TypeError(f"Cannot convert {type(v)} to Slice")

    def __repr__(self) -> str:
        return f"Slice({self.start}, {self.stop}, {self.step})"


class Dimensions(EventedModel):
    __root__: Dict[Union[int, str], Slice]

    def __init__(_model_self_, __root__: Any) -> None:
        super().__init__(__root__=__root__)

    def __repr__(self) -> str:
        return f"Dimensions({self.__root__!r})"

    @validator("__root__", pre=True)
    def _validate_root(cls, v: Any) -> dict[int | str, Slice]:
        if isinstance(v, (tuple, list, Sequence)):
            # Dimensions(range(3))
            # Dimensions([0, 1, 2])
            # Dimensions('ZYX')
            v = {i: None for i in v}
        if not isinstance(v, dict):
            raise TypeError(f"Cannot convert {type(v)} to Dimensions")
        for k in list(v):
            if v[k] is None:
                v[k] = Slice()
        return v


# thinking about this
# class WorldSlice(EventedModel):
#     slices: List[Slice] = []
