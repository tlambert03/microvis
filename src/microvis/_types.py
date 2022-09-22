from typing import Union, Literal, Tuple
import numpy as np

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
