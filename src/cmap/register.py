"""Functions to inject our Colormap instances into other libraries."""
from __future__ import annotations

import sys

from .colormap import Colormap
from .conversion import to_mpl, to_napari, to_vispy


def register_cmaps_with_matplotlib(*cmaps: Colormap) -> None:
    """Register specified/all Colormap instances with matplotlib.

    This allows the Colormap instance *itself* to be passed as
    as the `cmap` argument to matplotlib functions.

    If no Colormap instances are specified, all Colormap instances
    in the registry are registered.

    This function does nothing if matplotlib is not already imported.
    """
    if mpl := sys.modules.get("matplotlib"):
        for cmap in cmaps or _INSTANCES:
            if cmap not in mpl.colormaps:
                mpl.colormaps.register(to_mpl(cmap), name=str(cmap))


def register_cmaps_with_vispy(*cmaps: Colormap) -> None:
    """Register specified/all Colormap instances with vispy.

    This function does nothing if vispy is not already imported.
    """
    if "vispy" not in sys.modules:
        return
    from vispy.color import colormap

    colormap._colormaps.update({cm: to_vispy(cm) for cm in cmaps or _INSTANCES})


def register_cmaps_with_napari(*cmaps: Colormap) -> None:
    """Register specified/all Colormap instances with napari.

    This function does nothing if napari is not already imported.
    """
    if "napari" not in sys.modules:
        return
    from napari.utils import colormaps

    colormaps.AVAILABLE_COLORMAPS.update(
        {cm: to_napari(cm) for cm in cmaps or _INSTANCES}
    )
