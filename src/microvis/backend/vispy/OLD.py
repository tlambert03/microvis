from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    pass


ValidCamera = Literal["base", "panzoom", "perspective", "turntable", "fly", "arcball"]
