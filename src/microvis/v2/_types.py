from typing import Literal, Tuple, Union
from enum import Enum

import numpy as np
from pydantic.color import Color as Color


class CameraType(str, Enum):
    """Camera type."""

    ARCBALL = "arcball"
    PANZOOM = "panzoom"

    def __str__(self) -> str:
        return self.value


class UndefinedType:
    _instance = None

    def __new__(cls) -> "UndefinedType":
        """singleton"""
        if cls._instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __repr__(self) -> str:
        return "Undefined"

    def __bool__(self) -> bool:
        return False


Undefined = UndefinedType()


Color = Color
RGBTuple = Tuple[float, float, float]
RGBATuple = Tuple[float, float, float, float]
ClimString = Literal["auto"]
ValidClim = Union[ClimString, Tuple[float, float]]
ValidCmap = str
ArrayLike = np.ndarray

# fmt: off
ColorName = Literal[
    "k", "w", "r", "g", "b", "y", "m", "c", "aqua", "aliceblue", "antiquewhite",
    "black", "blue", "cyan", "darkblue", "darkcyan", "darkgreen", "darkturquoise",
    "deepskyblue", "green", "lime", "mediumblue", "mediumspringgreen", "navy",
    "springgreen", "teal", "midnightblue", "dodgerblue", "lightseagreen",
    "forestgreen", "seagreen", "darkslategray", "darkslategrey", "limegreen",
    "mediumseagreen", "turquoise", "royalblue", "steelblue", "darkslateblue",
    "mediumturquoise", "indigo", "darkolivegreen", "cadetblue", "cornflowerblue",
    "mediumaquamarine", "dimgray", "dimgrey", "slateblue", "olivedrab", "slategray",
    "slategrey", "lightslategray", "lightslategrey", "mediumslateblue", "lawngreen",
    "aquamarine", "chartreuse", "gray", "grey", "maroon", "olive", "purple",
    "lightskyblue", "skyblue", "blueviolet", "darkmagenta", "darkred", "saddlebrown",
    "darkseagreen", "lightgreen", "mediumpurple", "darkviolet", "palegreen",
    "darkorchid", "yellowgreen", "sienna", "brown", "darkgray", "darkgrey",
    "greenyellow", "lightblue", "paleturquoise", "lightsteelblue", "powderblue",
    "firebrick", "darkgoldenrod", "mediumorchid", "rosybrown", "darkkhaki", "silver",
    "mediumvioletred", "indianred", "peru", "chocolate", "tan", "lightgray",
    "lightgrey", "thistle", "goldenrod", "orchid", "palevioletred", "crimson",
    "gainsboro", "plum", "burlywood", "lightcyan", "lavender", "darksalmon",
    "palegoldenrod", "violet", "azure", "honeydew", "khaki", "lightcoral",
    "sandybrown", "beige", "mintcream", "wheat", "whitesmoke", "ghostwhite",
    "lightgoldenrodyellow", "linen", "salmon", "oldlace", "bisque", "blanchedalmond",
    "coral", "cornsilk", "darkorange", "deeppink", "floralwhite", "fuchsia", "gold",
    "hotpink", "ivory", "lavenderblush", "lemonchiffon", "lightpink", "lightsalmon",
    "lightyellow", "magenta", "mistyrose", "moccasin", "navajowhite", "orange",
    "orangered", "papayawhip", "peachpuff", "pink", "red", "seashell", "snow",
    "tomato", "white", "yellow", "transparent",
]
# fmt: on
# None means black and transparent
# str to allow "#FFF" hex strings
ValidColor = Union[None, ColorName, str, list, tuple, np.ndarray]
