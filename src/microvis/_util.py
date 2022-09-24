from __future__ import annotations
import contextlib
import numpy as np

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic.color import Color


def in_notebook() -> bool:
    """Determine if the user is executing in a Jupyter Notebook"""
    with contextlib.suppress(Exception):
        from IPython import get_ipython

        return get_ipython().__class__.__name__ == "ZMQInteractiveShell"
    return False


def in_ipython() -> bool:
    """Return true if we're running in an IPython interactive shell."""
    with contextlib.suppress(Exception):
        from IPython import get_ipython

        return get_ipython().__class__.__name__ == "TerminalInteractiveShell"
    return False


def color_to_np(color: Color | None) -> np.ndarray | None:
    """Convert a color to a hex string."""
    if color is None:
        return None
    c = np.asarray(color.as_rgb_tuple())
    c[:3] = c[:3] / 255
    return c
