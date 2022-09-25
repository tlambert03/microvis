"""package description."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("microvis")
except PackageNotFoundError:
    __version__ = "uninstalled"
__author__ = "Talley Lambert"
__email__ = "talley.lambert@gmail.com"

from .convenience import imshow
from .core import Camera, Canvas, Image, Scene, View


__all__ = ["Camera", "Canvas", "Image", "Scene", "View", "imshow"]
