from typing import Any

from vispy import scene

from ..._types import CameraType
from ...core.nodes import camera, node
from ._node import Node


class Camera(Node, camera.CameraBackend):
    _native: scene.cameras.BaseCamera

    def __init__(self, camera: camera.Camera, **backend_kwargs: Any) -> None:
        cam = scene.cameras.make_camera(str(camera.type))
        self._native = cam

    def _viz_get_native(self) -> Any:
        return self._native

    def _viz_add_node(self, node: node.Node) -> None:
        raise NotImplementedError

    def _viz_set_interactive(self, arg: bool) -> None:
        raise NotImplementedError()

    def _viz_set_zoom(self, arg: float) -> None:
        raise NotImplementedError()

    def _viz_set_center(self, arg: tuple[float, ...]) -> None:
        raise NotImplementedError()

    def _viz_set_type(self, arg: CameraType) -> None:
        assert isinstance(self._native.parent, scene.ViewBox)
        self._native.parent.camera = str(arg)

    def _viz_reset(self) -> None:
        self._native.set_range(margin=0)
