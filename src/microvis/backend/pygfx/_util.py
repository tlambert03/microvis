from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from microvis._types import Color


def pyd_color_to_vispy(color: Color | None) -> str:
    """Convert a color to a hex string."""
    return color.as_hex() if color is not None else "black"
