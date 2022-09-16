"""package description."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("microvis")
except PackageNotFoundError:
    __version__ = "uninstalled"
__author__ = "Talley Lambert"
__email__ = "talley.lambert@gmail.com"

from .core import imshow, ortho
from .viewer import Viewer

__all__ = ["Viewer", "imshow", "ortho"]
