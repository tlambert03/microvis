from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pydantic.color import Color


def pyd_color_to_vispy(color: Color | None) -> str | None:
    """Convert a color to a hex string."""
    return color.as_hex() if color is not None else None
