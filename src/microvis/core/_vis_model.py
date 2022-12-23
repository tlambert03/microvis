from __future__ import annotations

from abc import abstractmethod
from importlib import import_module
from typing import Any, ClassVar, Dict, Generic, Optional, Protocol, Type, \
    TypeVar, cast

import numpy as np
from psygnal import EmissionInfo, EventedModel
from psygnal.containers import EventedList
from pydantic.fields import Field, PrivateAttr

from microvis._logger import logger

__all__ = ["Field", "VisModel", "ModelBase", "SupportsVisibility"]

SETTER_METHOD = "_vis_set_{name}"


class ModelBase(EventedModel):
    """Base class for all pydantic-style models."""

    class Config:
        extra = "ignore"
        validate_assignment = True
        allow_property_setters = True
        json_encoders = {EventedList: lambda x: list(x),
                         np.ndarray: np.ndarray.tolist}


F = TypeVar("F", covariant=True, bound="VisModel")


class BackendAdaptor(Protocol[F]):
    """Protocol for backend adaptor classes."""

    @abstractmethod
    def __init__(self, obj: F, **backend_kwargs: Any) -> None:
        """All backend adaptor objects recieve the object they are adapting."""
        ...

    @abstractmethod
    def _vis_get_native(self) -> Any:
        """Return the native widget for the backend."""

    # TODO: add a "detach" or "cleanup" method?


class SupportsVisibility(BackendAdaptor[F], Protocol):
    """Protocol for objects that support visibility (show/hide)."""

    @abstractmethod
    def _vis_set_visible(self, arg: bool) -> None:
        """Set the visibility of the object."""


T = TypeVar("T", bound=BackendAdaptor)


class VisModel(ModelBase, Generic[T]):
    """Front end object driving a backend interface.

    This is an important class.  Most things subclass this.  It provides the event
    connection between the model object and a backend adaptor.

    A backend adaptor is a class that implements the BackendAdaptor protocol (of type
    `T`... for which this class is a generic). The backend adaptor is an object
    responsible for converting all of the microvis protocol methods (stuff like
    "_vis_set_width", "_vis_set_visible", etc...) into the appropriate calls for
    the given backend.

    TODO: looks like we assume a single backend adaptor per object.
    But that feels like a limitation.  We might want to have multiple
    backend adaptors per object.
    """

    # Really, this should be `_backend: ClassVar[Optional[T]]``, but that a type error
    # PEP 526 states that ClassVar cannot include any type variables...
    # but there is discussion that this might be too limiting.
    # dicsussion: https://github.com/python/mypy/issues/5144
    _backend_adaptor: ClassVar[Optional[Any]] = PrivateAttr(None)

    # This is an optional class variable that can be set by subclasses to
    # provide a mapping of backend names to backend adaptor classes.
    # see `examples/custom_node.py` for an example of how this is used.
    BACKEND_ADAPTORS: ClassVar[Dict[str, Type[BackendAdaptor]]]

    @property
    def has_adaptor(self) -> bool:
        """Return True if the object has a backend adaptor."""
        return self._backend_adaptor is not None

    def backend_adaptor(self) -> T:
        """Get the backend adaptor for this object. Creates one if it doesn't exist."""
        # if we make this a property, it will be cause the side effect of
        # spinning up a backend on tab auto-complete in ipython/jupyter
        if self._backend_adaptor is None:
            backend_cls = self._get_adaptor_type()
            # The type error is that we can't assign to a Class Variable.
            # However, if we don't mark `_backend` as a Class
            self._backend_adaptor = self._create_adaptor(
                backend_cls)  # type: ignore [misc]
        return cast("T", self._backend_adaptor)

    @property
    def native(self) -> Any:
        """Return the native object of the backend."""
        return self.backend_adaptor()._vis_get_native()

    def _get_adaptor_type(
        self,
        backend: str = "",
        class_name: str = "",
    ) -> Type[T]:
        """Retrieves the backend class with the same name as the object class name."""
        # TODO: we're mostly just falling back on vispy here all the time for
        # early development, but it needs to be clearer how one would pick
        # a different backend.  (though... the default behavior should be to
        # pick the "right" backend for the current environment.  i.e. microvis
        # should work with no configuration in both jupyter and ipython desktop.)
        backend = backend or _get_default_backend()

        if hasattr(self,
                   "BACKEND_ADAPTORS") and backend in self.BACKEND_ADAPTORS:
            adaptor_class = self.BACKEND_ADAPTORS[backend]
            logger.debug(f"Using class-provided adaptor class: {adaptor_class}")
        else:
            class_name = class_name or type(self).__name__
            backend_module = import_module(f"...backend.{backend}", __name__)
            adaptor_class = getattr(backend_module, class_name)

        return cast(Type[T], self.validate_adaptor_class(adaptor_class))

    @classmethod
    def validate_adaptor_class(
        cls, adaptor_class: Any
    ) -> type[BackendAdaptor]:
        """Validate that the adaptor class is appropriate for the core object."""
        # NOTE: if the hashability of either cls or backend_class is ever an issue,
        # this might not need to be cached, or `cls` could be replaced with a frozenset
        # of signal names.
        # todo: readd cache in pydantic friendly manner
        model_class = cls
        logger.debug(
            f"Validating adaptor class {adaptor_class} for {model_class}")
        if missing := {
            SETTER_METHOD.format(name=field.name)
            for field in model_class.__fields__.values()
            if
            not hasattr(adaptor_class, SETTER_METHOD.format(name=field.name))
        }:
            raise ValueError(
                f"{adaptor_class} cannot be used as a backend object for "
                f"{model_class}: it is missing the following setters: {missing}"
            )
        return cast("Type[BackendAdaptor]", adaptor_class)

    def _create_adaptor(self, cls: Type[T]) -> T:
        """Instantiate the backend adaptor object.

        The purpose of this method is to allow subclasses to override the
        creation of the backend object. Or do something before/after.
        """
        logger.debug(f"Attaching {type(self)} to backend {cls}")
        return cls(self)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # if using this in an EventedModel, connect to the events
        if hasattr(self, "events"):
            self.events.connect(self._on_any_event)

    def _on_any_event(self, info: EmissionInfo) -> None:
        if not self.has_adaptor:
            return

        args = info.args
        signal_name = info.signal.name

        try:
            name = SETTER_METHOD.format(name=signal_name)
            setter = getattr(self._backend_adaptor, name)
        except AttributeError as e:
            logger.exception(e)
            return

        event_name = f"{type(self).__name__}.{signal_name}"
        logger.debug(f"{event_name}={args} emitting to backend")

        try:
            setter(*args)
        except Exception as e:
            logger.exception(e)

    # TODO:
    # def detach(self) -> None:
    #     """Disconnect and destroy the backend adaptor from the object."""
    #     self._backend = None


def _get_default_backend() -> str:
    """Stub function for the concept of picking a backend when none is specified.

    This will likely be context dependent.
    """
    return "vispy"
