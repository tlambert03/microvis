from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING, Any, Literal, Optional, cast

from vispy import scene
from ._base import CanvasBase, ViewBase

if TYPE_CHECKING:
    from pydantic.color import Color
    import numpy as np

    from .._types import ValidClim, ValidCmap, ValidColor

ValidCamera = Literal["base", "panzoom", "perspective", "turntable", "fly", "arcball"]




from microvis import _interface

