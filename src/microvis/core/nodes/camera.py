from __future__ import annotations

from abc import abstractmethod
from typing import Protocol

from microvis._types import CameraType
from microvis.core._base import Field, FrontEndFor

from .node import Node, NodeBackend


class Camera(Node, FrontEndFor["CameraBackend"]):
    """A camera that defines the view of a scene."""

    type: CameraType = Field(CameraType.PANZOOM, description="Camera type.")
    interactive: bool = Field(
        default=True,
        description="Whether the camera responds to user interaction, "
        "such as mouse and keyboard events.",
    )
    zoom: float = Field(1.0, description="Zoom factor of the camera.")
    center: tuple[float, float, float] | tuple[float, float] = Field(
        (0, 0, 0), description="Center position of the view."
    )


# fmt: off
class CameraBackend(NodeBackend[Camera], Protocol):
    """Protocol for a backend camera adapter object."""

    @abstractmethod
    def _vis_set_type(self, arg: CameraType) -> None: ...
    @abstractmethod
    def _vis_set_zoom(self, arg: float) -> None: ...
    @abstractmethod
    def _vis_set_center(self, arg: tuple[float, ...]) -> None: ...
# fmt: on
