from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from .. import schema
from .._protocols import CameraBackend, FrontEndFor, ViewBackend
from ._image import Image
from ._node import Node

if TYPE_CHECKING:
    from typing import Any

    import numpy as np


class Scene(Node):
    ...


class Camera(FrontEndFor[CameraBackend], schema.Camera):
    def reset(self) -> None:
        self._backend._viz_reset()


class View(FrontEndFor[ViewBackend], schema.View):
    camera: Camera = Field(default_factory=Camera)
    scene: Scene = Field(default_factory=Scene)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.scene._backend = self._backend._viz_get_scene()
        self.camera._backend = self._backend._viz_get_camera()

    def add_image(self, data: np.ndarray, **kwargs: Any) -> None:
        img = Image(data, **kwargs)
        self.scene.add(img)
        self.camera.reset()
        return img
