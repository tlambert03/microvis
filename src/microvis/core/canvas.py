from __future__ import annotations

import warnings
from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol

from psygnal.containers import EventedList

from .._types import Color
from ._base import Field, FrontEndFor, SupportsVisibility
from .view import View

if TYPE_CHECKING:
    from typing import Any

    import numpy as np


# fmt: off
class CanvasBackend(SupportsVisibility['Canvas'], Protocol):
    """Backend interface for Canvas."""

    @abstractmethod
    def _viz_set_width(self, arg: int) -> None: ...
    @abstractmethod
    def _viz_set_height(self, arg: int) -> None: ...
    @abstractmethod
    def _viz_set_size(self, arg: tuple[int, int]) -> None: ...
    @abstractmethod
    def _viz_set_background_color(self, arg: Color | None) -> None: ...
    @abstractmethod
    def _viz_set_title(self, arg: str) -> None: ...
    @abstractmethod
    def _viz_close(self) -> None: ...
    @abstractmethod
    def _viz_render(self) -> np.ndarray: ...
    @abstractmethod
    def _viz_add_view(self, view: View) -> None: ...
# fmt: on


class ViewList(EventedList[View]):
    def _pre_insert(self, value: View) -> View:
        if not isinstance(value, View):
            raise TypeError("Canvas views must be View objects")
        return super()._pre_insert(value)


class Canvas(FrontEndFor[CanvasBackend]):
    """Canvas onto which views are rendered."""

    width: float = Field(500, description="The width of the canvas in pixels.")
    height: float = Field(500, description="The height of the canvas in pixels.")
    background_color: Color | None = Field(
        None,
        description="The background color. None implies transparent "
        "(which is usually black)",
    )
    visible: bool = Field(False, description="Whether the canvas is visible.")
    title: str = Field("", description="The title of the canvas.")
    views: EventedList[View] = Field(default_factory=EventedList, allow_mutation=False)

    @property
    def size(self) -> tuple[float, float]:
        """Return the size of the canvas."""
        return self.width, self.height

    # FIXME: this @size.setter convenience is triggering a double event to the backend
    # and requires an extended protocol above
    # perhaps modify FrontEndFor event handler to skip derived fields?
    @size.setter
    def size(self, value: tuple[float, float]) -> None:
        """Set the size of the canvas."""
        self.width, self.height = value

    def close(self) -> None:
        """Close the canvas."""
        if self.has_backend:
            self.backend_adaptor()._viz_close()

    # show and render will trigger a backend connection

    def show(self) -> None:
        """Show the canvas."""
        self.backend_adaptor()  # make sure backend is connected
        self.visible = True

    def hide(self) -> None:
        """Hide the canvas."""
        self.visible = False

    def render(self) -> np.ndarray:
        """Render canvas to offscren buffer and return as numpy array."""
        # TODO: do we need to set visible=True temporarily here?
        return self.backend_adaptor()._viz_render()

    # consider using canavs.views.append?
    def add_view(self, view: View | None = None, **kwargs: Any) -> View:
        """Add a new view to the canvas."""
        # TODO: change kwargs to params
        if view is None:
            view = View(**kwargs)
        elif not isinstance(view, View):
            raise TypeError("view must be an instance of View")
        elif kwargs:
            warnings.warn("kwargs ignored when view is provided")

        self.views.append(view)
        if self.has_backend:
            self.backend_adaptor()._viz_add_view(view)

        return view

    def _repr_mimebundle_(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Return a mimebundle for the canvas."""
        if hasattr(self.native, "_repr_mimebundle_"):
            return self.native._repr_mimebundle_(*args, **kwargs)  # type: ignore
        return NotImplemented


class GridCanvas(Canvas):
    """Subclass with numpy-style indexing."""

    # def __getitem__(self, key: tuple[int, int]) -> View:
    #     """Get the View at the given row and column."""
