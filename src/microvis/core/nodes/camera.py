from __future__ import annotations

from abc import abstractmethod
from typing import Literal, Protocol

from microvis._types import CameraType
from microvis.core._transform import Transform
from microvis.core._vis_model import VisModel

from .node import Node, NodeAdaptorProtocol

# Parameters
# ----------
# fov: float
#     The field of view as an angle in degrees. Higher values give a
#     wide-angle lens effect. This value is limited between 0 and
#     179. If zero, it operates in orthographic mode. Default 50.
# aspect: float
#     The desired aspect ratio, which is used to determine the vision pyramid's
#     boundaries depending on the viewport size. Common values are 16/9 or 4/3. Default 1.
# width: float
#     The width of the scene to view. If omitted or None, the width
#     is derived from aspect and height.
# height: float
#     The height of the scene to view. If omitted or None, the height
#     is derived from aspect and width.
# zoom: float
#     An additional zoom factor, equivalent to attaching a zoom lens.
# maintain_aspect: bool
#     Whether the aspect ration is maintained as the window size changes.
#     Default True. If false, the dimensions are stretched to fit the window.
# depth_range: 2-tuple
#     The values for the near and far clipping planes. If not given
#     or None, the clip planes will be calculated automatically based
#     on the fov, width, and height.

# "scale": self.local.scale,
# "zoom": self.zoom,

# "width": self.width
# "height": self.height


class Camera(Node, VisModel["CameraAdaptorProtocol"]):
    # Node.tranform controls
    # - the position of the camera in the world
    # - the orientation (up direction and view direction)
    fov: float = 45  # vertical field of view
    near_clip: float | None = None  # distance from camera position to near clip plane
    far_clip: float | None = None  # distance from camera position to far clip plane

    aspect: float = 1  # ?  probably remove from camera... glean from view
                       # but look at vispy and pygfx to see how they handle this
    maintain_aspect: bool = True  # this is just a motion rule...
    moving_fov_moves: Literal["camera", "viewbox"] = "camera"
    # in 'camera' mode

    # the camera is allowed to move as fov changes, while maintaining height/width
    # viewbox(port).  So, transform will have to change...

    # in viewbox mode, the camera position/transform stays fixed, and the viewbox will
    # necessarily change size as fov changes.

    def look_at(self, position: tuple[float, float, float]) -> None:
        """Set the camera to look at a given position."""
        # would update the transform to point the camera at the given position
        raise NotImplementedError

    def perspective_matrix(self) -> Transform:
        # defined by vertical_fov, near_clip, far_clip
        # near/far clip along with fov give you 8 points
        # 8 points define a frustum
        
        # fov-angle either defines the shape of the frustum
        # or the frustum defines the fov-angle  (can't have both)
        raise NotImplementedError

    def orthographic_matrix(self) -> Transform:
        raise NotImplementedError

    def perspective_projection_matrix(self) -> Transform:
        """Map scene into the canonical view volume."""
        return self.orthographic_matrix() @ self.perspective_matrix()


# class Camera(Node, VisModel["CameraAdaptorProtocol"]):
# """A camera that defines the view of a scene.

# The purpose of a camera is to define the viewpoint for rendering a scene.
# This viewpoint consists of its position (in the world) and its projection_matrix.
# """

# projection_matrix: Transform = Field(
#     default_factory=Transform, description="Projection matrix."
# )

# type: CameraType = Field(default=CameraType.PANZOOM, description="Camera type.")
# interactive: bool = Field(
#     default=True,
#     description="Whether the camera responds to user interaction, "
#     "such as mouse and keyboard events.",
# )

# @property
# def position(self) -> Tuple[float, float, float]:
#     """The viewpoint in 3D - what the camera is looking at.

#     If we name scene dimensions (z, y, x) to match image dimensions (d, h, w) then
#     this should be a (z, y, x) coordinate in the world space
#     """

# @property
# def zoom(self) -> float:
#     """The zoom factor of the camera.

#     A zoom of 1 means 1 px on screen has the same area as 1 unscaled 2D image pixel
#     in world space.
#     """

# @property
# def view_direction(self) -> Tuple[float, float, float]:
#     """The direction in which the camera is looking.

#     If you draw a line into the scene from the center of the View through the scene,
#     it would move through `Camera.position` along the `Camera.view_direction`.

#     In the local coordinate system of the camera, this is typically defined as the
#     -z direction of the camera object.
#     """

# @property
# def up_direction(self) -> Tuple[float, float, float]:
#     """The direction that is considered "up" in the scene.

#     up_direction is perpendicular to the view direction and corresponds to the y
#     axis (h dimension) of the canvas. It should be defined such that drawing a line
#     straight up from the center of the View moves from Camera.position along
#     up_direction.
#     """
#     # Note: The setter on up_direction doesn't have to be perfectly perpendicular,
#     # you can project a provided vector into the xy-plane of the camera and use
#     # that as the up_direction

# def reset_rotation(self) -> None:
#     """Reset rotation to default."""

# def rotate_x(self, theta: float) -> None:
#     """Rotate the camera around the x axis by `theta` degrees."""

# def rotate_y(self, theta: float) -> None:
#     """Rotate the camera around the y axis by `theta` degrees."""

# def rotate_z(self, theta: float) -> None:
#     """Rotate the camera around the z axis by `theta` degrees."""

# def _set_range(self, margin: float = 0) -> None:
#     if self.has_backend_adaptor("vispy"):
#         adaptor = self.backend_adaptor()
#         # TODO: this method should probably be pulled off of the backend,
#         # calculated directly in the core, and then applied as a change to the
#         # camera transform
#         adaptor._vis_set_range(margin=margin)


# fmt: off
class CameraAdaptorProtocol(NodeAdaptorProtocol[Camera], Protocol):
    """Protocol for a backend camera adaptor object."""

    @abstractmethod
    def _vis_set_type(self, arg: CameraType) -> None: ...
    @abstractmethod
    def _vis_set_projection_matrix(self, arg: Transform) -> None: ...
    @abstractmethod
    def _vis_set_range(self, margin: int) -> None: ...
# fmt: on
