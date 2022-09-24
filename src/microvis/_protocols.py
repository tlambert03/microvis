from __future__ import annotations
from abc import abstractmethod

import importlib
from typing import TYPE_CHECKING, Any, Generic, Optional, Protocol, TypeVar
from psygnal import SignalGroup, EmissionInfo
from pydantic.color import Color
from ._logs import logger

if TYPE_CHECKING:
    import numpy as np
    from . import core


T = TypeVar("T", bound="Backend")


def _get_backend_instance(obj: object, backend_kwargs: dict, backend: str = "") -> Any:
    backend = backend or "vispy"  # TODO
    backend_module = importlib.import_module(f"microvis.backend.{backend}")
    backend_obj = getattr(backend_module, type(obj).__name__)
    return backend_obj(obj, **backend_kwargs)


class FrontEndFor(Generic[T]):
    """Front end object driving a backend interface."""

    events: SignalGroup

    def __init__(self, *args: Any, **kwargs: Any):
        backend_kwargs = kwargs.pop("backend_kwargs", None) or {}
        super().__init__(*args, **kwargs)
        self._backend: T = _get_backend_instance(self, backend_kwargs)
        name = f"{type(self).__module__}.{type(self).__qualname__}"
        bkname = f"{type(self._backend).__module__}.{type(self._backend).__qualname__}"
        logger.debug(f"attaching {name!r} to backend object {bkname!r}")
        self.events.connect(self._on_any_event)

    def _on_any_event(self, info: EmissionInfo) -> None:
        setter = getattr(self._backend, f"_viz_set_{info.signal.name}")
        event_name = f"{type(self).__name__}.{info.signal.name}"
        logger.debug(f"{event_name}={info.args} emitted to backend")
        setter(*info.args)

    @property
    def native(self) -> Any:
        """Return the native object of the backend."""
        return self._backend._viz_get_native()


class Backend(Protocol):
    @abstractmethod
    def _viz_get_native(self) -> Any:
        """Return the native widget for the backend."""


class SupportsVisibility(Protocol):
    @abstractmethod
    def _viz_set_visible(self, arg: bool) -> None:
        """Set the visibility of the object."""


# fmt: off
class CanvasBackend(Backend, SupportsVisibility, Protocol):
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


class ViewBackend(Backend, SupportsVisibility, Protocol):
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
# fmt: on
