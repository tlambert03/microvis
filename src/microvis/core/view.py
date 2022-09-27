from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Protocol, Tuple, TypeVar

from .._types import ArrayLike, Color
from ._base import Field, FrontEndFor
from .nodes import Camera, Image, Scene
from .nodes.node import Node, NodeBackend

if TYPE_CHECKING:
    from .canvas import Canvas

NodeType = TypeVar("NodeType", bound=Node)


# fmt: off
class ViewBackend(NodeBackend['View'], Protocol):
    """Protocol for the backend of a View."""

    @abstractmethod
    def _viz_set_camera(self, arg: Camera) -> None: ...
    @abstractmethod
    def _viz_set_scene(self, arg: Scene) -> None: ...
    @abstractmethod
    def _viz_set_position(self, arg: tuple[float, float]) -> None: ...
    @abstractmethod
    def _viz_set_size(self, arg: tuple[float, float] | None) -> None: ...
    @abstractmethod
    def _viz_set_background_color(self, arg: Color | None) -> None: ...
    @abstractmethod
    def _viz_set_border_width(self, arg: float) -> None: ...
    @abstractmethod
    def _viz_set_border_color(self, arg: Color | None) -> None: ...
    @abstractmethod
    def _viz_set_padding(self, arg: int) -> None: ...
    @abstractmethod
    def _viz_set_margin(self, arg: int) -> None: ...
# fmt: on


class View(Node, FrontEndFor[ViewBackend]):
    """A rectangular area on a canvas that displays a scene, with a camera."""

    _BackendProtocol: ClassVar[type] = ViewBackend

    camera: Camera = Field(default_factory=Camera)
    scene: Scene = Field(default_factory=Scene)  # necessary additional layer?

    # TODO:
    # position and size are problematic...
    # they are given in pixels, but whenever the canvas is redrawn,
    # their meaning changes. also vispy will overwrite position and size (with .rect)
    # on resize events.
    # consider making these fractional values (0-1) and then scaling them to the canvas
    position: Tuple[float, float] = Field(
        default=(0, 0),
        description="The position of the view with respect to its canvas",
    )
    size: Optional[Tuple[float, float]] = Field(
        default=None,
        description="The size of the scene. None implies size of parent canvas",
    )

    background_color: Optional[Color] = Field(
        default=None,
        description="The background color. None implies transparent.",
    )
    border_width: float = Field(
        default=0,
        description="The width of the border line in pixels.",
    )
    border_color: Optional[Color] = Field(None, description="The color of the border.")
    padding: int = Field(
        default=0,
        description="The amount of padding in the widget "
        "(i.e. the space reserved between the contents and the border).",
    )
    margin: int = Field(
        default=0,
        description="The margin to keep outside the widget's border.",
    )

    def show(self) -> Canvas:
        """Show the view.

        Convenience method for showing the canvas that the view is on.
        If no canvas exists, a new one is created.
        """
        from .canvas import Canvas

        # TODO: we need to know/check somehow if the view is already on a canvas
        canvas = Canvas()
        canvas.add_view(self)
        canvas.show()
        return canvas

    def add_node(self, node: NodeType) -> NodeType:
        """Add any node to the scene."""
        self.scene.add(node)
        if self.camera.has_backend:
            self.camera.native.set_range(margin=0)  # TODO
        return node

    def add_image(self, data: ArrayLike, **kwargs: Any) -> Image:
        """Add an image to the scene."""
        return self.add_node(Image(data, **kwargs))
