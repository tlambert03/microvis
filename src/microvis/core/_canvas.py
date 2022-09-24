from __future__ import annotations

import warnings
from typing import TYPE_CHECKING
from .._protocols import FrontEndFor, CanvasBackend
from .. import schema
from ._view import View

if TYPE_CHECKING:
    import numpy as np
    from typing import Any


class Canvas(FrontEndFor[CanvasBackend], schema.Canvas):
    # consider composing rather than inheriting the schema

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def size(self) -> tuple[float, float]:
        """Return the size of the canvas."""
        return self.width, self.height

    def set_size(self, value: tuple[float, float]) -> None:
        """Set the size of the canvas."""
        self.width, self.height = value

    def close(self) -> None:
        """Close the canvas."""
        self._backend._viz_close()

    def show(self) -> None:
        """Show the canvas."""
        self._backend._viz_set_visible(True)

    def render(self) -> np.ndarray:
        """Render canvas to offscren buffer and return as numpy array."""
        return self._backend._viz_render()

    def add_view(self, view: View | None = None, **kwargs: Any) -> View:
        """Add a new view to the canvas."""
        # TODO: change kwargs to params
        if view is None:
            view = View(**kwargs)
        elif kwargs:
            warnings.warn("kwargs ignored when view is provided")

        self._backend._viz_add_view(view)
        return view
