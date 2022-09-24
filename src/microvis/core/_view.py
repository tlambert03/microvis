from __future__ import annotations

from typing import TYPE_CHECKING
from .._protocols import FrontEndFor, ViewBackend
from .. import schema
from pydantic import Field


if TYPE_CHECKING:
    from typing import Any


class Scene(schema.Scene):
    ...


class Camera(schema.Camera):
    ...


class View(FrontEndFor[ViewBackend], schema.View):
    camera: schema.Camera = Field(default_factory=Camera)
    scene: schema.Scene = Field(default_factory=Scene)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
