from __future__ import annotations

from abc import abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generator,
    Protocol,
    Sequence,
    SupportsIndex,
    TypeVar,
)

from psygnal import EventedModel
from pydantic import validator

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


class Slice(EventedModel):
    start: float | None = Field(default=None)
    stop: float | None = Field(default=None)
    step: float | None = Field(default=None)

    def __init__(_model_self_, *args: float, **data: float) -> None:
        if args:
            if data:
                raise TypeError("Cannot pass both args and kwargs")
            _slc = slice(*args)
            data = {"start": _slc.start, "stop": _slc.stop, "step": _slc.step}
        super().__init__(**data)

    def indices(self, length: SupportsIndex) -> tuple[int, int, int]:
        """
        This method takes a single integer argument length and computes
        information about the slice that the slice object would describe if
        applied to a sequence of length items. It returns a tuple of three
        integers; respectively these are the start and stop indices and the
        step or stride length of the slice. Missing or out-of-bounds indices
        are handled in a manner consistent with regular slices.
        """
        return slice(self.start, self.stop, self.step).indices(length)

    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> Slice:
        if v is None:
            return cls()
        if isinstance(v, slice):
            return cls(start=v.start, stop=v.stop, step=v.step)
        if isinstance(v, (int, float)):
            return cls(v)
        raise TypeError(f"Cannot convert {type(v)} to Slice")

    def __repr__(self) -> str:
        return f"Slice({self.start}, {self.stop}, {self.step})"


class Dimensions(EventedModel):
    __root__: dict[int | str, Slice]

    def __init__(_model_self_, __root__: Any) -> None:
        super().__init__(__root__=__root__)

    def __repr__(self) -> str:
        return f"Dimensions({repr(self.__root__)})"

    @validator("__root__", pre=True)
    def _validate_root(cls, v: Any) -> dict[int | str, Slice]:
        if isinstance(v, (tuple, list, Sequence)):
            # Dimensions(range(3))
            # Dimensions([0, 1, 2])
            # Dimensions('ZYX')
            v = {i: None for i in v}
        if isinstance(v, dict):
            for k in list(v):
                if v[k] is None:
                    v[k] = Slice()
        return v  # type: ignore


class View(Node, FrontEndFor[ViewBackend]):
    """A rectangular area on a canvas that displays a scene, with a camera."""

    camera: Camera = Field(default_factory=Camera)
    scene: Scene = Field(default_factory=Scene)  # necessary additional layer?

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.add(self.camera)
        self.add(self.scene)

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        if name in {"camera", "scene"}:
            self.add(getattr(self, name))

    # TODO:
    # position and size are problematic...
    # they are given in pixels, but whenever the canvas is redrawn,
    # their meaning changes. also vispy will overwrite position and size (with .rect)
    # on resize events.
    # consider making these fractional values (0-1) and then scaling them to the canvas
    position: tuple[float, float] = Field(
        default=(0, 0),
        description="The position of the view with respect to its canvas",
    )
    size: tuple[float, float] | None = Field(
        default=None,
        description="The size of the scene. None implies size of parent canvas",
    )

    background_color: Color | None = Field(
        default=None,
        description="The background color. None implies transparent.",
    )
    border_width: float = Field(
        default=0,
        description="The width of the border line in pixels.",
    )
    border_color: Color | None = Field(None, description="The color of the border.")
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

    def add(self, node: Node) -> None:
        """Add any node to the scene."""
        # View is a special case of Node, only accepts top level
        if not isinstance(node, (Camera, Scene)):
            raise TypeError(
                f"View can only contain a Camera and a Scene, not {type(node)}"
            )
        return super().add(node)
