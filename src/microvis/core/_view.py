from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from .. import schema
from .._protocols import CameraBackend, FrontEndFor, NodeBackend, ViewBackend
from ._image import Image

if TYPE_CHECKING:
    from typing import Any

    import numpy as np


class Scene(FrontEndFor[NodeBackend], schema.Scene):
    def add(self, obj: schema.Node) -> None:
        pass


class Camera(FrontEndFor[CameraBackend], schema.Camera):
    ...


class View(FrontEndFor[ViewBackend], schema.View):
    camera: Camera = Field(default_factory=Camera)
    scene: Scene = Field(default_factory=Scene)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.scene._backend = self._backend._viz_get_scene()
        self.camera._backend = self._backend._viz_get_camera()

    def add_image(self, data: np.ndarray, **kwargs: Any) -> None:
        img = Image(data)
        self.scene.add(img)
