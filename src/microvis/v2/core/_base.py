from abc import abstractmethod
from importlib import import_module
from typing import Any, Generic, Protocol, TypeVar

from psygnal import EmissionInfo, EventedModel
from pydantic import Field as Field
from pydantic.fields import PrivateAttr

from ..._logs import logger


class ModelBase(EventedModel):
    """Base class for all pydantic-style models."""

    class Config:
        extra = "ignore"
        validate_assignment = True
        allow_property_setters = True


F = TypeVar("F", covariant=True, bound="FrontEndFor")


class BackendAdaptor(Protocol[F]):
    """Protocol for backend adaptor classes."""

    @abstractmethod
    def __init__(self, obj: F, **backend_kwargs: Any) -> None:
        ...

    @abstractmethod
    def _viz_get_native(self) -> Any:
        """Return the native widget for the backend."""

    # TODO: add a "detach" or "cleanup" method?


class SupportsVisibility(BackendAdaptor[F], Protocol):
    """Protocol for objects that support visibility (show/hide)."""

    @abstractmethod
    def _viz_set_visible(self, arg: bool) -> None:
        """Set the visibility of the object."""


T = TypeVar("T", bound=BackendAdaptor)


class FrontEndFor(ModelBase, Generic[T]):
    """Front end object driving a backend interface."""

    _backend: T | None = PrivateAttr(None)

    @property
    def has_backend(self) -> bool:
        return self._backend is not None

    def backend_adaptor(self) -> T:
        # if we make this a property, it will be cause the side effect of
        # spinning up a backend on tab auto-complete in ipython/jupyter
        if self._backend is None:
            self._backend = self._attach_backend()
        return self._backend

    @property
    def native(self) -> Any:
        """Return the native object of the backend."""
        return self.backend_adaptor()._viz_get_native()

    def _attach_backend(
        self, backend_kwargs: dict | None = None, backend: str = ""
    ) -> T:
        """Retrieves the backend class with the same name as the object class name."""
        backend = backend or "vispy"  # TODO
        backend_module = import_module(f"...backend.{backend}", __name__)
        backend_class: type[T] = getattr(backend_module, type(self).__name__)

        logger.debug(f"Attaching {self} to backend {backend_class}")
        return backend_class(self, **(backend_kwargs or {}))

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # if using this in an EventedModel, connect to the events
        if hasattr(self, "events"):
            self.events.connect(self._on_any_event)

    def _on_any_event(self, info: EmissionInfo) -> None:
        if not self.has_backend:
            return
        try:
            name = f"_viz_set_{info.signal.name}"
            setter = getattr(self._backend, name)
        except AttributeError:
            logger.critical(f"{type(self._backend)} has no attribute {name!r}")
            return

        event_name = f"{type(self).__name__}.{info.signal.name}"
        logger.debug(f"{event_name}={info.args} emitting to backend")

        setter(*info.args)
