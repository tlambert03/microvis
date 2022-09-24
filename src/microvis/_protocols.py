from __future__ import annotations

from abc import abstractmethod
from importlib import import_module
from typing import TYPE_CHECKING, Any, Generic, Optional, Protocol, TypeVar

from ._logs import logger

if TYPE_CHECKING:
    import numpy as np
    from psygnal import EmissionInfo, SignalGroup

    from . import core
    from ._types import Color


T = TypeVar("T", bound="_Backend")


def _get_backend_instance(obj: object, backend_kwargs: dict, backend: str = "") -> Any:
    """Retrieves the backend class with the same name as the object class name."""
    backend = backend or "vispy"  # TODO
    backend_module = import_module(f"microvis.backend.{backend}")
    backend_obj = getattr(backend_module, type(obj).__name__)
    return backend_obj(obj, **backend_kwargs)


class FrontEndFor(Generic[T]):
    """Front end object driving a backend interface."""

    events: SignalGroup

    def __init__(self, *args: Any, **kwargs: Any):
        backend_kwargs = kwargs.pop("backend_kwargs", None) or {}
        super().__init__(*args, **kwargs)
        self._backend: T = _get_backend_instance(self, backend_kwargs)
        if hasattr(self, "events"):
            self.events.connect(self._on_any_event)

    def _on_any_event(self, info: EmissionInfo) -> None:
        setter = getattr(self._backend, f"_viz_set_{info.signal.name}")
        event_name = f"{type(self).__name__}.{info.signal.name}"
        logger.debug(f"{event_name}={info.args} emitting to backend")

        setter(*info.args)

    @property
    def native(self) -> Any:
        """Return the native object of the backend."""
        return self._backend._viz_get_native()


class _Backend(Protocol):
    @abstractmethod
    def _viz_get_native(self) -> Any:
        """Return the native widget for the backend."""


class _SupportsVisibility(_Backend, Protocol):
    @abstractmethod
    def _viz_set_visible(self, arg: bool) -> None:
        """Set the visibility of the object."""


# fmt: off
class CanvasBackend(_SupportsVisibility, Protocol):
    @abstractmethod
    def __init__(self, canvas: core.Canvas, **backend_kwargs: Any): ...
    @abstractmethod
    def _viz_set_width(self, arg: int) -> None: ...
    @abstractmethod
    def _viz_set_height(self, arg: int) -> None: ...
    @abstractmethod
    def _viz_set_background_color(self, arg: Optional[Color]) -> None: ...
    @abstractmethod
    def _viz_set_title(self, arg: str) -> None: ...
    @abstractmethod
    def _viz_close(self) -> None: ...
    @abstractmethod
    def _viz_render(self) -> np.ndarray: ...
    @abstractmethod
    def _viz_add_view(self, view: core.View) -> None: ...


class ViewBackend(_SupportsVisibility, Protocol):
    @abstractmethod
    def __init__(self, view: core.View, **backend_kwargs: Any): ...
    @abstractmethod
    def _viz_set_camera(self, arg: core.Camera) -> None: ...
    @abstractmethod
    def _viz_set_scene(self, arg: core.Scene) -> None: ...
    @abstractmethod
    def _viz_set_position(self, arg: tuple[float, float]) -> None: ...
    @abstractmethod
    def _viz_set_size(self, arg: Optional[tuple[float, float]]) -> None: ...
    @abstractmethod
    def _viz_set_background_color(self, arg: Optional[Color]) -> None: ...
    @abstractmethod
    def _viz_set_border_width(self, arg: float) -> None: ...
    @abstractmethod
    def _viz_set_border_color(self, arg: Optional[Color]) -> None: ...
    @abstractmethod
    def _viz_set_padding(self, arg: int) -> None: ...
    @abstractmethod
    def _viz_set_margin(self, arg: int) -> None: ...
    @abstractmethod
    def _viz_get_scene(self) -> NodeBackend: ...
    @abstractmethod
    def _viz_get_camera(self) -> CameraBackend: ...


class NodeBackend(_SupportsVisibility, Protocol):
    def _viz_add_node(self, node: core.Node) -> None: ...

class CameraBackend(NodeBackend, Protocol):
    def _viz_set_interactive(self, arg: bool) -> None: ...
    def _viz_set_zoom(self, arg: float) -> None: ...
    def _viz_set_center(self, arg: tuple[float, ...]) -> None: ...


class ImageBackend(_SupportsVisibility, Protocol):
    ...

# fmt: on
