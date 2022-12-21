from __future__ import annotations

from abc import abstractmethod
from functools import lru_cache
from importlib import import_module
from typing import Any, ClassVar, Generic, Protocol, TypeVar, cast, List, Dict

import numpy as np
from psygnal import EmissionInfo, EventedModel
from psygnal.containers import EventedList
from pydantic.fields import Field, PrivateAttr

from microvis._logger import logger

__all__ = ["Field", "FrontEndFor", "ModelBase", "SupportsVisibility"]

SETTER_METHOD = "_viz_set_{name}"


class ModelBase(EventedModel):
    """Base class for all pydantic-style models."""

    class Config:
        extra = "ignore"
        validate_assignment = True
        allow_property_setters = True
        json_encoders = {EventedList: lambda x: list(x),
                         np.ndarray: np.ndarray.tolist}


F = TypeVar("F", covariant=True, bound="FrontEndFor")


class BackendAdaptor(Protocol[F]):
    """Protocol for backend adaptor classes."""

    @abstractmethod
    def __init__(self, obj: F, **backend_kwargs: Any) -> None:
        """All backend adaptor objects recieve the object they are adapting."""
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
    """Front end object driving a backend interface.

    This is an important class.  Most things subclass this.  It provides the event
    connection between the model object and backend adaptors.

    A backend adaptor is a class that implements the BackendAdaptor protocol (of type
    `T`... for which this class is a generic). The backend adaptor is an object
    responsible for converting all of the microvis protocol methods (stuff like
    "_viz_set_width", "_viz_set_visible", etc...) into the appropriate calls for
    the given backend.

    TODO: looks like we assume a single backend adaptor per object.
    But that feels like a limitation.  We might want to have multiple
    backend adaptors per object.
    """

    _backends: List[T] = PrivateAttr([])
    _backend_lookup: ClassVar[dict[str, type[BackendAdaptor]]] = {}

    @property
    def has_backend(self) -> bool:
        """Return True if the object has backend adaptor(s)."""
        return len(self._backends) > 0

    def backend_adaptors(self) -> List[T]:
        """Get the backend adaptor for this object. Creates one if it doesn't exist."""
        # if we make this a property, it will be cause the side effect of
        # spinning up a backend on tab auto-complete in ipython/jupyter
        if not self.has_backend:
            self._backends.append(self._get_backend_obj())
        return self._backends

    @property
    def native_objects(self) -> Dict[T, Any]:
        """Return the native object of the backend."""
        return {
            type(adaptor): adaptor._viz_get_native()
            for adaptor
            in self.backend_adaptors()
        }

    def _get_backend_obj(
        self,
        backend_kwargs: dict | None = None,
        backend: str = "",
        class_name: str = "",
    ) -> T:
        """Retrieves the backend class with the same name as the object class name."""
        # TODO: we're mostly just falling back on vispy here all the time for
        # early development, but it needs to be clearer how one would pick
        # a different backend.  (though... the default behavior should be to
        # pick the "right" backend for the current environment.  i.e. microvis
        # should work with no configuration in both jupyter and ipython desktop.)
        backend = backend or "vispy"

        if backend in self._backend_lookup:
            backend_class = self._backend_lookup[backend]
            logger.debug(f"Using class-provided backend class: {backend_class}")
        else:
            class_name = class_name or type(self).__name__
            backend_module = import_module(f"...backend.{backend}", __name__)
            backend_class = getattr(backend_module, class_name)

        # TODO: fix TypeGuard
        backend_class = validate_backend_class(type(self), backend_class)
        logger.debug(f"Attaching {type(self)} to backend {backend_class}")
        return cast("T", backend_class(self, **(backend_kwargs or {})))

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # if using this in an EventedModel, connect to the events
        if hasattr(self, "events"):
            self.events.connect(self._on_any_event)

    def _on_any_event(self, info: EmissionInfo) -> None:
        if not self.has_backend:
            return

        args = info.args
        signal_name = info.signal.name

        try:
            name = SETTER_METHOD.format(name=signal_name)
            setter = getattr(self._backends, name)
        except AttributeError as e:
            logger.exception(e)
            return

        event_name = f"{type(self).__name__}.{signal_name}"
        logger.debug(f"{event_name}={args} emitting to backend")

        try:
            setter(*args)
        except Exception as e:
            logger.exception(e)


@lru_cache
def validate_backend_class(cls: type[FrontEndFor], backend_class: type[T]) -> \
    type[T]:
    """Validate that the backend class is appropriate for the object."""
    logger.debug(f"Validating backend class {backend_class} for {cls}")
    if missing := {
        SETTER_METHOD.format(name=signal._name)
        for signal in cls.__signal_group__._signals_.values()
        if not hasattr(backend_class, SETTER_METHOD.format(name=signal._name))
    }:
        raise ValueError(
            f"{backend_class} cannot be used as a backend object for {cls}: "
            f"it is missing the following setters: {missing}"
        )
    return backend_class
