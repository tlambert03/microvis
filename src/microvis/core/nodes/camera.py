from __future__ import annotations

from abc import abstractmethod
from typing import Protocol, Tuple, Union

from microvis._types import CameraType
from microvis.core._vis_model import Field, VisModel

from .node import Node, NodeAdaptorProtocol


class Camera(Node, VisModel["CameraAdaptorProtocol"]):
    """A camera that defines the view of a scene."""

    type: CameraType = Field(default=CameraType.PANZOOM, description="Camera type.")
    interactive: bool = Field(
        default=True,
        description="Whether the camera responds to user interaction, "
        "such as mouse and keyboard events.",
    )
    zoom: float = Field(default=1.0, description="Zoom factor of the camera.")
    center: Union[Tuple[float, float, float], Tuple[float, float]] = Field(
        default=(0, 0, 0), description="Center position of the view."
    )


# fmt: off
class CameraAdaptorProtocol(NodeAdaptorProtocol[Camera], Protocol):
    """Protocol for a backend camera adaptor object."""

    @abstractmethod
    def _vis_set_type(self, arg: CameraType) -> None: ...
    @abstractmethod
    def _vis_set_zoom(self, arg: float) -> None: ...
    @abstractmethod
    def _vis_set_center(self, arg: tuple[float, ...]) -> None: ...
# fmt: on
