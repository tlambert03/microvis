# flake8: noqa
# Visuals: drawable objects intended to encapsulate simple graphic objects
# such as lines, meshes, points, 2D shapes, images, text, etc.
from __future__ import annotations

from enum import Enum
from typing import Any, Literal, TypeVar, Union

import numpy as np
from pydantic import BaseModel, Field


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return str(self.value)


W = TypeVar("W", bound="Widget")
Color = Union[str, tuple[float, float, float, float], np.ndarray]

class Visual(BaseModel):
    """Visual that can be drawn using a single shader program."""

    # fcode: str = Field(description="Fragment shader code")
    # vcode: str = Field(description="Vertex shader code")
    # gcode: str | None = Field(None, description="Geometry shader code")

    # def set_gl_state(self, preset=None, **kwargs): ...
    # def update_gl_state(self, *args, **kwargs): ...
    # def draw(self): ...
    # def attach(self, filt, view=None): ...
    #     """Attach a Filter to this visual."""
    # def detach(self, filt, view=None): ...
    #     """Detach a Filter from this visual."""

class Colormap(BaseModel):
    """Colormap that relates intensity values to colors."""

    name: str = ""
    colors: list[Color] = Field(description="The list of control colors.")
    controls: list[float] = Field(
        description="Sorted, increasing control points for given colors."
        "Must start with 0 and end with 1. If len(controls) == len(colors), linear "
        "interpolation is used between each color. If len(controls) == len(colors) + 1,"
        " colors are defined by the value of the color in the bin between by "
        "neighboring controls points."
    )

class ImageRenderMethod(StrEnum):
    """Image nonlinear method."""

    auto = "auto"
    subdivide = "subdivide"
    impostor = "impostor"

class ImageInterpolation(StrEnum):
    """Image interpolation method."""

    bessel = "bessel"
    blackman = "blackman"
    catrom = "catrom"
    cubic = "cubic"
    gaussian = "gaussian"
    hamming = "hamming"
    hanning = "hanning"
    hermite = "hermite"
    kaiser = "kaiser"
    lanczos = "lanczos"
    linear = "linear"
    mitchell = "mitchell"
    nearest = "nearest"
    quadric = "quadric"
    sinc = "sinc"
    spline16 = "spline16"
    spline36 = "spline36"

class Image:
    data: np.ndarray
    clim: tuple[float, float] = (0, 1)
    cmap: Colormap = "gray"
    interpolation_method: Literal["nearest", "linear"] = "nearest"

class _ImageBase(Visual):
    cmap: Colormap = Field("gray", description="Colormap to use for the image.")
    clim: tuple[float, float] | None = Field(
        None, description="Limits to use for the colormap. `None` implies autoscale."
    )
    gamma: float = Field(1.0, description="Gamma correction to apply to the image.")
    interpolation: ImageInterpolation = Field(
        "nearest", description="Image interpolation method."
    )

class ImageVisual(_ImageBase):
    """Visual that draws a 2D image."""

    data: np.ndarray = Field(
        description="2D Image data. Can be shape (M, N), (M, N, 3), or (M, N, 4), for "
        "grayscale, RGB, or RGBA images, respectively."
    )
    method: ImageRenderMethod = Field(
        description="Image rendering method for non-linear transforms. "
        "If the transform is linear, this parameter is ignored and a single quad is "
        "drawn around the area of the image"
    )
    complex_mode: Literal["real", "imaginary", "magnitude", "phase"] = Field(
        "magnitude",
        description="The mode used to convert complex valued data to a scalar.",
    )

    # grid: tuple[int, int] = Field(description="Grid size for subdivide method")
    # custom_kernel: np.ndarray = np.ones((1, 1))
    # def set_data(self, image: np.ndarray) -> None: ...

class VolumeRenderMethod(StrEnum):
    """Volume rendering method."""

    mip = "mip"
    attenuated_mip = "attenuated_mip"
    minip = "minip"
    translucent = "translucent"
    additive = "additive"
    iso = "iso"
    average = "average"

class VolumeVisual(_ImageBase):
    """Visual that draws a 3D volume."""

    data: np.ndarray = Field(description="Must be ndim==3, assumed to be (Z, Y, X).")
    method: VolumeRenderMethod = Field("mip", description="Volume rendering method.")
    threshold: float | None = Field(
        None, description="Threshold for iso method. Where `None` implies data.mean()"
    )
    attenuation: float = Field(1, description="Attenuation for attenuated_mip method.")
    relative_step_size: float = Field(
        0.8,
        description="The relative step size to step through the volume. "
        "Larger values yield higher performance at reduced quality. If "
        "set > 2.0 the ray skips entire voxels. Recommended values are "
        "between 0.5 and 1.5. The amount of quality degredation depends "
        "on the render method.",
    )
    mip_cutoff: float = Field(
        np.finfo("float32").min,
        description="Cutoff for MIP method. None implies no cutoff.",
    )
    minip_cutoff: float = Field(
        np.finfo("float32").max,
        description="The upper cutoff value for `minip` "
        "(None should be coerced to max float value).",
    )
    raycasting_mode: Literal["volume", "plane"] = Field(
        "volume",
        description="Whether to cast a ray through the whole volume or perpendicular "
        "to a plane through the volume defined.",
    )
    # only for plane mode
    plane_position: tuple[float, float, float] | None = Field(None)
    plane_normal: tuple[float, float, float] | None = Field(None)
    plane_thickness: float = Field(
        ge=1,
        description="A value defining the total length of the ray perpendicular to the "
        "plane interrogated during rendering. Defined in data coordinates. "
        "Only relevant in raycasting_mode = 'plane'.",
    )

coords = np.ndarray

class BaseTransform(BaseModel):
    """Defines a pair of complementary coordinate mapping functions (map and imap)
    in both python and GLSL."""

    # def map(self, obj: coords) -> coords:
    # def imap(self, obj: coords) -> coords:

class Node(BaseModel):
    """Base class representing an object in a scene.

    A group of nodes connected through parent-child relationships define a
    scenegraph. Nodes may have any number of children.

    With the ``transform`` property, each Node implicitly defines a "local"
    coordinate system, and the Nodes and edges in the scenegraph can be thought
    of as coordinate systems connected by transformation functions.
    """

    parent: Node | None = Field(None, description="Parent node.")
    name: str | None = Field(None, description="Name of the node.")
    transform: BaseTransform | None = Field(
        None,
        description="Transform that maps the local coordinate frame to the coordinate "
        "frame of the parent.",
    )
    picking: bool = Field(
        False,
        description="whether this node (and its children) are drawn in picking mode.",
    )

    visible: bool = Field(True, description="Whether this node is visible.")
    opacity: float = Field(1.0, description="Opacity of this node.", ge=0, le=1)
    clip_children: bool = Field(
        description="Whether children of this node will inherit its clipper"
    )
    order: int = Field(
        0,
        description="A value used to determine the order in which nodes are drawn. "
        "Greater values are drawn later. Children are always drawn after their parent",
    )
    document: Node | None = Field(
        None,
        description="Optional coordinate system from which this node should make "
        "physical measurements such as px, mm, pt, in, etc. If `None` (default), a "
        "default document is used during drawing",
    )
    document_node: Node | None = Field(
        None,
        description="The node to be used as the document coordinate system. "
        "`None` implies that the document node is `self.root_node`",
    )

    # canvas: Canvas | None  # derived from parent

class VisualNode(Node):
    interactive: bool = Field(
        False, description="Whether this widget accepts mouse and touch events"
    )
    def draw(self): ...

class ImageNode(VisualNode, ImageVisual): ...
class VolumeNode(VisualNode, VolumeVisual): ...

class CompoundVisual(Visual):
    subvisuals: list[Visual] = Field()

class CompoundNode(VisualNode, CompoundVisual): ...

# widget is just a compound node with convenience methods
class Widget(CompoundNode):
    """A widget takes up a rectangular space, intended for use in
    a 2D pixel coordinate frame.

    The widget is positioned using the transform attribute (as any
    node), and its extent (size) is kept as a separate property."""

    pos: tuple[float, float] = Field(
        description="A 2-element tuple to specify the top left corner of the widget."
    )

    size: tuple[float, float] = Field(
        description="A 2-element tuple to spicify the size of the widget."
    )
    border_color: Color = Field(description="The color of the border.")
    border_width: float = Field(description="The width of the border line in pixels.")
    bgcolor: Color = Field(description="The background color")
    padding: int = Field(
        description="The amount of padding in the widget "
        "(i.e. the space reserved between the contents and the border)."
    )
    margin: int = Field(description="The margin to keep outside the widget's border.")

    def add_view(self, *args, **kwargs) -> ViewBox:
        return self.add_widget(ViewBox(*args, **kwargs))
    def add_grid(self, *args, **kwargs) -> Grid:
        return self.add_widget(Grid(*args, **kwargs))
    def add_widget(self, widget: W) -> W:
        """add widget to self._widgets and reparent the widget to self"""

# Views and Grids

class BaseCamera(Node): ...
class SubScene(Node): ...

class ViewBox(Widget):
    """Provides a Camera."""

    camera: BaseCamera = Field(description="Camera in use by this ViewBox")
    scene: SubScene

    def add(self, node: Node) -> None:
        """same as node.parent = viewbox.scene"""

class Grid(Widget):
    def __getitem__(self, key: tuple[int, int]) -> Widget: ...
    def add_widget(
        self,
        widget: Widget | None = None,
        row: int | None = None,
        col: int | None = None,
        row_span: int = 1,
        col_span: int = 1,
        **widget_kwargs: Any,
    ) -> Widget: ...

# Canvas
from vispy.scene import SceneCanvas


class SceneCanvas:
    """A Canvas that automatically draws the contents of a scene"""

    title: str
    size: tuple[int, int]
    position: tuple[int, int]
    show: bool
    bgcolor: Color
    resizeable: bool
    fullscreen: bool

    # scene: SubScene = SubScene()
    # central_widget: Widget = Widget(parent=self.scene)

    # def update(self): ...
    # def close(self): ...
    # def show(self): ...

    def draw_visual(self, visual: Node, event=None):
        """Draw a visual and its children to the canvas or currently active
        framebuffer."""
    def render(self, region=None, size=None, bgcolor=None, crop=None, alpha=True):
        """Render the scene to an offscreen buffer and return the image array."""
    def update(self, event=None):
        """Inform the backend that the Canvas needs to be redrawn"""
