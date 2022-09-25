from __future__ import annotations

from abc import abstractmethod
from typing import Optional, Protocol

from .._types import Color
from ._base import Field, FrontEndFor
from .nodes import Camera, Scene
from .nodes.node import Node, NodeBackend


class View(Node, FrontEndFor["ViewBackend"]):
    """A rectangular area on the screen that displays a scene, with a camera."""

    camera: Camera = Field(default_factory=Camera)
    scene: Scene = Field(default_factory=Scene)

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
    size: Optional[tuple[float, float]] = Field(
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

    # def __init__(self, *args: Any, **kwargs: Any):
    #     super().__init__(*args, **kwargs)
    #     self.scene._backend = self._backend._viz_get_scene()
    #     self.camera._backend = self._backend._viz_get_camera()

    # def add_image(self, data: np.ndarray, **kwargs: Any) -> None:
    #     img = Image(data, **kwargs)
    #     self.scene.add(img)
    #     self.camera.reset()
    #     return img


# fmt: off
class ViewBackend(NodeBackend[View], Protocol):
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
    # @abstractmethod
    # def _viz_get_scene(self) -> NodeBackend: ...
    # @abstractmethod
    # def _viz_get_camera(self) -> CameraBackend: ...

# fmt: on
