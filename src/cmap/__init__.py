# from .colormap import Colormap
# # from .colormaps import green
# from .register import (
#     register_cmaps_with_matplotlib,
#     register_cmaps_with_napari,
#     register_cmaps_with_vispy,
# )

# __all__ = [
#     "Colormap",
#     "register_cmaps_with_matplotlib",
#     "register_cmaps_with_napari",
#     "register_cmaps_with_vispy",
#     "green",
# ]

from .color import Color
from .colormap import LinearColormap

__all__ = ["Color", "LinearColormap"]
