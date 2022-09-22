from __future__ import annotations

from typing import cast
from ._types import ValidClim, ValidCmap, ClimString


def clim(obj: object) -> ValidClim:
    allowable: tuple[str] = getattr(ClimString, "__args__", ())
    if isinstance(obj, str):
        if obj not in allowable:
            raise ValueError(f"Invalid clim string {obj!r}. Must be one of {allowable}")
        return cast("ValidClim", obj)
    elif isinstance(obj, tuple):
        if len(obj) != 2:
            raise ValueError("clim must be a tuple of length 2")
        return (float(obj[0]), float(obj[1]))
    raise ValueError(f"clim must be a tuple of length 2 or one of {allowable}")


def cmap(obj: object) -> ValidCmap | None:
    if isinstance(obj, str):
        return obj
    if obj is None:
        return None
    raise ValueError("cmap must be a string")
