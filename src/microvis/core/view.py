from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Optional, Protocol, Tuple, TypeVar

from microvis._types import ArrayLike, Color

from ._vis_model import Field
from .nodes import Camera, Image, Scene
from .nodes.node import Node, NodeAdaptorProtocol

if TYPE_CHECKING:
    from .canvas import Canvas

NodeType = TypeVar("NodeType", bound=Node)


# fmt: off
class ViewAdaptorProtocol(NodeAdaptorProtocol['View'], Protocol):
    """Protocol defining the interface for a View adaptor."""

    @abstractmethod
    def _vis_set_camera(self, arg: Camera) -> None: ...
    @abstractmethod
    def _vis_set_scene(self, arg: Scene) -> None: ...
    @abstractmethod
    def _vis_set_position(self, arg: tuple[float, float]) -> None: ...
    @abstractmethod
    def _vis_set_size(self, arg: tuple[float, float] | None) -> None: ...
    @abstractmethod
    def _vis_set_background_color(self, arg: Color | None) -> None: ...
    @abstractmethod
    def _vis_set_border_width(self, arg: float) -> None: ...
    @abstractmethod
    def _vis_set_border_color(self, arg: Color | None) -> None: ...
    @abstractmethod
    def _vis_set_padding(self, arg: int) -> None: ...
    @abstractmethod
    def _vis_set_margin(self, arg: int) -> None: ...
# fmt: on


def _make_camera() -> Camera:
    return Camera()


def _make_scene() -> Scene:
    return Scene()


class View(Node[ViewAdaptorProtocol]):
    """A rectangular area on a canvas that displays a scene, with a camera.

    A canvas can have one or more views. Each view has a single scene (i.e. a
    scene graph of nodes) and a single camera. The camera defines the view
    transformation.

    Outside of these two primary properties, a view has a number of other aesthetic
    properties like position, size, border, padding, and margin (which follows the
    CSS box model).

        position
        |
        v
    --->+--------------------------------+  ^
        |            margin              |  |
        |  +--------------------------+  |  |
        |  |         border           |  |  |
        |  |  +--------------------+  |  |  |
        |  |  |      padding       |  |  |  |
        |  |  |  +--------------+  |  |  |   height
        |  |  |  |   content    |  |  |  |  |
        |  |  |  |              |  |  |  |  |
        |  |  |  +--------------+  |  |  |  |
        |  |  +--------------------+  |  |  |
        |  +--------------------------+  |  |
        +--------------------------------+  v

        <------------ width ------------->
    """

    camera: Camera = Field(default_factory=_make_camera)
    scene: Scene = Field(default_factory=_make_scene)  # necessary additional layer?

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
    # TODO: canvas has height and width, but view has size. should this be consistent?
    size: Optional[Tuple[float, float]] = Field(
        default=None,
        description="The size of the scene. None implies size of parent canvas",
    )

    background_color: Optional[Color] = Field(
        default=None,
        description="The background color (inside of the border). "
        "None implies transparent.",
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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.add(self.camera)
        self.add(self.scene)

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        if name in {"camera", "scene"}:
            self.add(getattr(self, name))

    def show(self) -> Canvas:
        """Show the view.

        Convenience method for showing the canvas that the view is on.
        If no canvas exists, a new one is created.
        """
        from .canvas import Canvas

        # TODO: we need to know/check somehow if the view is already on a canvas
        # This just creates a new canvas every time
        canvas = Canvas()
        canvas.add_view(self)
        canvas.show()
        return canvas

    def add_node(self, node: NodeType) -> NodeType:
        """Add any node to the scene."""
        self.scene.add(node)
        self.camera._set_range(margin=0)
        return node

    def add_image(self, data: ArrayLike, **kwargs: Any) -> Image:
        """Add an image to the scene."""
        return self.add_node(Image(data, **kwargs))

    def add(self, node: Node) -> None:
        """Add any node to the scene."""
        # View is a special case of Node, only accepts top level
        if not isinstance(node, (Camera, Scene)):  # pragma: no cover
            raise TypeError(
                f"View can only contain a Camera and a Scene, not {type(node)}"
            )
        return super().add(node)

    def _create_adaptor(self, cls: type[ViewAdaptorProtocol]) -> ViewAdaptorProtocol:
        adaptor = super()._create_adaptor(cls)
        adaptor._vis_set_scene(self.scene)
        adaptor._vis_set_camera(self.camera)
        return adaptor
