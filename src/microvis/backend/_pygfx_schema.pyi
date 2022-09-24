from __future__ import annotations
import enum
from typing import Any, Callable, Literal
from pygfx.objects import Event
import numpy as np

# wgpu provides canvases for:
# - Offscreen
# - jupyter (vis jupyter-rfb)
# - glfw (vis glfw)
# - qt (via pyside/PyQt)

class Canvas:
    size: tuple[int, int]  # "logical size"
    title: str

    # base interface
    def draw_frame(self) -> None: ...
    def request_draw(self, draw_function: Callable | None = None) -> None:
        """Request from the main loop to schedule a new draw event"""
    def get_pixel_ratio(self) -> float:
        """Get the logical size in float pixels."""
    def get_physical_size(self) -> tuple[int, int]:
        """Get the physical size in integer pixels."""
    def get_logical_size(self) -> tuple[float, float]:
        """Get the logical size in float pixels."""
    def set_logical_size(self, width: float, height: float) -> None:
        """Set the window size (in logical pixels)."""
    def close(self) -> None:
        """Close the window."""
    def is_closed(self) -> bool:
        """Get whether the window is closed."""
    def get_context(self, kind: str = "gpupresent"): ...
    # autogui interface
    def handle_event(self, event: Event) -> None:
        """Handle a single event."""
    def add_event_handler(self, *args: Any) -> Any:
        """Register an event handler."""
    def remove_event_handler(self, callback: Callable, *types: str) -> None:
        """Unregister an event handler."""

Matrix3x4 = np.ndarray
Matrix4x4 = np.ndarray

class Geometry:
    """A geometry object contains the data that defines (the shape of) the
    object, such as positions, plus data associated with these positions
    (normals, texcoords, colors, etc.)."""

    indices: np.ndarray | None  # typically Nx3 for mesh geometry
    positions: np.ndarray | None  # Nx3 positions (xyz) defining location of verts
    normals: np.ndarray | None  # Nx3 normal vectors
    texcoords: np.ndarray | None  # Nx1, Nx2 or Nx3, to lookup color for a vertex
    colors: np.ndarray | None  # per-vertex colors NxM with M 1-4 depending on type
    sizes: list[float]  # scalar per-vertex size
    # A 2D or 3D Texture/TextureView that contains a regular grid of
    # data. I.e. for images and volumes.
    grid: np.ndarray | None

    def bounding_box(self) -> np.ndarray: ...
    def bounding_sphere(self) -> np.ndarray: ...

class Material:
    """Materials define how an object is rendered, subject to certain properties."""

    opacity: float = 1
    clipping_planes: list[Matrix3x4] = []
    # If this is "ANY" (the default) a fragment is discarded
    # if it is clipped by any clipping plane. If this is "ALL", a
    # fragment is discarded only if it is clipped by *all* of the
    # clipping planes.
    clipping_mode: Literal["any", "all"] = "any"

    # uniform_buffer:

class RenderMask(enum.IntFlag):
    # Indicates in what render passes to render this object:
    # * "auto": try to determine the best approach (default).
    # * "opaque": only in the opaque render pass.
    # * "transparent": only in the transparent render pass(es).
    # * "all": render in both opaque and transparent render passses.
    auto = 0
    opaque = 1
    transparent = 2
    all = 3

class WorldObject:
    """The base class for objects present in the "world", i.e. the scene graph."""

    geometry: Geometry
    material: Material
    parent: WorldObject | None = None
    children: list[WorldObject] = []
    matrix: Matrix4x4

    # these are composed from matrix
    # position = Vector3()
    # rotation = Quaternion()
    # scale = Vector3(1, 1, 1)

    visible: bool = True
    render_order: int = 0
    render_mask: RenderMask = RenderMask.auto

    matrix_auto_update: bool = True  # whether matrix auto updates

    def add(self, *children: WorldObject) -> None:
        """Add children to this object."""
    def remove(self, *children: WorldObject) -> None:
        """Remove children from this object."""
    def clear(self) -> None:
        """Remove all children from this object."""
    def traverse(self, callback: Callable) -> None:
        """Traverse the scene graph, calling a callback for each object."""

class Camera(WorldObject):
    """
    The purpose of a camera is to define the viewpoint for rendering a scene.
    This viewpoint consists of its position (in the world) and its projection.
    """
    # matrix_world_inverse = Matrix4()
    # projection_matrix = Matrix4()
    # projection_matrix_inverse = Matrix4()


class Renderer:
    def render(
        self,
        scene: WorldObject,
        camera: Camera,
        *,
        rect=None,
        viewport=None,
        clear_color=None,
        flush=True,
    ):
        """Render a scene with the specified camera as the viewpoint."""
    def flush(self) -> None:
        """Render the result into the target texture view"""
