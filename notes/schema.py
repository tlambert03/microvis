from __future__ import annotations

from typing import List, Optional, Tuple, Union

from psygnal import EventedModel
from pydantic import Field, PrivateAttr
from pydantic.color import Color

from microvis._types import CameraType


class ModelBase(EventedModel):
    _backend = PrivateAttr()

    class Config:
        extra = "ignore"
        validate_assignment = True


class Transform(ModelBase):
    """Tranformation matrix mapping one coordinate frame to another."""


class Node(ModelBase):
    """World object in a scene graph."""

    name: Optional[str] = Field(None, description="Name of the node.")
    parent: Optional[Node] = Field(
        None, description="Parent node. If None, this node is a root node."
    )
    children: List[Node] = Field(default_factory=list)
    visible: bool = Field(True, description="Whether this node is visible.")
    opacity: float = Field(default=1.0, ge=0, le=1, description="Opacity of this node.")
    order: int = Field(
        0,
        description="A value used to determine the order in which nodes are drawn. "
        "Greater values are drawn later. Children are always drawn after their parent",
    )
    interactive: bool = Field(
        False, description="Whether this node accepts mouse and touch events"
    )
    transform: Optional[Transform] = Field(
        None,
        description="Transform that maps the local coordinate frame to the coordinate "
        "frame of the parent.",
    )

    # picking: bool = Field(
    #     False,
    #     description="whether this node (and its children) are drawn in picking mode.",
    # )
    # clip_children: bool = Field(
    #     description="Whether children of this node will inherit its clipper"
    # )


class Camera(Node):
    """Camera that views a scene."""

    type: CameraType = Field(CameraType.PANZOOM, description="Camera type.")
    interactive: bool = Field(
        default=True,
        description="Whether the camera responds to user interaction, "
        "such as mouse and keyboard events.",
    )
    zoom: float = Field(1.0, description="Zoom factor of the camera.")
    center: Union[Tuple[float, float, float], Tuple[float, float]] = Field(
        (0, 0, 0), description="Center position of the view."
    )
    # flip : tuple of bools
    #     For each dimension, specify whether it is flipped.
    # up : {'+z', '-z', '+y', '-y', '+x', '-x'}
    #     The direction that is considered up. Default '+z'. Not all
    #     camera's may support this (yet).


class PanZoomCamera(Camera):
    """i.e. 2D Orthographic Camera."""

    aspect_ratio: Optional[float] = Field(
        1,
        description="The ratio between the x and y dimension. If None, the dimensions "
        "are scaled automatically, dependening on the available space",
    )


class PerspectiveCamera(Camera):
    """3D Perspective Camera."""

    fov: float = Field(
        0,
        description="Field of view in degrees. Zero (default) means orthographic "
        "projection.",
    )
    distance: Optional[float] = Field(
        description="The distance of the camera from the rotation point (only makes "
        "sense if fov > 0). If None (default) the distance is determined from the"
        "zoom and fov."
    )
    angles: Tuple[float, float, float] = (0.0, 0.0, 90.0)


# data objects
class Affine(ModelBase):
    scale: float = Field(default=1.0, ge=0.0)
    translate: float = Field(default=0.0)
    rotate: float = Field(default=0.0)
    shear: float = Field(default=0.0)


class LayerDisplay(ModelBase):
    metadata: dict = Field(default_factory=dict)
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    blending: str = Field(default="translucent")


class VolumeDisplay(LayerDisplay):
    interpolation3d: str = "nearest"
    rendering: str = "mip"
    iso_threshold: float = Field(default=0.5, gt=0.0)
    attenuation: float = Field(default=0.05, gt=0.0)


class Image2DDisplay(LayerDisplay):
    cmap: str = "gray"  # TODO
    clim: Optional[Tuple[float, float]] = None  # where none means auto
    gamma: float = 1
    interpolation: str = "nearest"
    visible: bool = True


class ImageNode(Image2DDisplay, VolumeDisplay, Node):
    ...


# scene graph
class Scene(Node):
    """Root node of a scene graph."""


class View(Node):  # should it be a node?
    """Rectangular region of a scene that provides a view onto a Scene."""

    camera: Camera
    scene: Scene

    # TODO:
    # position and size are problematic...
    # they are given in pixels, but whenever the canvas is redrawn,
    # their meaning changes. also vispy will overwrite position and size (with .rect)
    # on resize events.
    # consider making these fractional values (0-1) and then scaling them to the canvas
    position: tuple[float, float] = Field(
        (0, 0),
        description="The position of the view with respect to its canvas",
    )
    size: Optional[tuple[float, float]] = Field(
        None,
        description="The size of the scene. None implies size of parent canvas",
    )

    background_color: Optional[Color] = Field(
        None, description="The background color. None implies transparent."
    )
    border_width: float = Field(
        0, description="The width of the border line in pixels."
    )
    border_color: Optional[Color] = Field(None, description="The color of the border.")
    padding: int = Field(
        0,
        description="The amount of padding in the widget "
        "(i.e. the space reserved between the contents and the border).",
    )
    margin: int = Field(
        0, description="The margin to keep outside the widget's border."
    )


class Canvas(ModelBase):
    """Canvas onto which a scene is rendered. Top level window."""

    width: float = Field(500, description="The width of the canvas in pixels.")
    height: float = Field(500, description="The height of the canvas in pixels.")
    background_color: Optional[Color] = Field(
        None,
        description="The background color. None implies transparent "
        "(which is usually black)",
    )
    visible: bool = Field(True, description="Whether the canvas is visible.")
    title: str = Field("", description="The title of the canvas.")

    # each of these scenes has some position on the canvas...
    # e.g. in vispy's SceneCanvas there is a single subScene
    #   ... that has a centra Widget (Compound Node)
    #   ... that has a ViewBox (ViewBox(Widget))
    #   ... that has a subScene
    #   ... that has a camera (which is itself a node)
    views: list[View] = Field(default_factory=list)

    # ??
    # mode: str = "2D", "grid", "ortho" ??
    # size = (width, height)
    # pixel_scale: float


class GridCanvas(Canvas):
    """Subclass with numpy-style indexing."""

    def __getitem__(self, key: tuple[int, int]) -> View:
        """Get the View at the given row and column."""
