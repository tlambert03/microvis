from typing import Any

from ._types import ArrayLike
from .core import Canvas


def imshow(image: ArrayLike, **kwargs: Any) -> Canvas:
    """Display an image."""
    canvas = Canvas()
    canvas.show()
    view = canvas.add_view()
    view.add_image(image, **kwargs)
    return canvas
