from __future__ import annotations

from abc import abstractmethod
from importlib import import_module
from typing import Any, ClassVar, Dict, Generic, Protocol, Set, Type, TypeVar, cast

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
        json_encoders = {EventedList: list, np.ndarray: np.ndarray.tolist}


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


AdaptorType = TypeVar("AdaptorType", bound=BackendAdaptor, covariant=True)


class VisModel(ModelBase, Generic[AdaptorType]):
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

    # Really, this should be `_backend: ClassVar[dict[str, T]]``, but thats a type error
    # PEP 526 states that ClassVar cannot include any type variables...
    # but there is discussion that this might be too limiting.
    # dicsussion: https://github.com/python/mypy/issues/5144
    _backend_adaptors: ClassVar[Dict[str, BackendAdaptor]] = PrivateAttr({})
    # This is the set of all field names that must have setters in the backend adaptor.
    # set during the init
    _evented_fields: ClassVar[Set[str]] = PrivateAttr(set())
    # this is a cache of all adaptor classes that have been validated to implement
    # the correct methods (via validate_adaptor_class).
    _validated_adaptor_classes: ClassVar[Set[Type]] = PrivateAttr(set())

    # This is an optional class variable that can be set by subclasses to
    # provide a mapping of backend names to backend adaptor classes.
    # see `examples/custom_node.py` for an example of how this is used.
    BACKEND_ADAPTORS: ClassVar[Dict[str, Type[BackendAdaptor]]]

    @property
    def has_adaptor(self) -> bool:
        """Return True if the object has a backend adaptor."""
        # TODO: this might need to turn into a method that accepts a backend name
        return bool(self._backend_adaptors)

    def backend_adaptor(self, backend: str | None = None) -> AdaptorType:
        """Get the backend adaptor for this object. Creates one if it doesn't exist.

        Parameters
        ----------
        backend : str, optional
            The name of the backend to use, by default None.  If None, the default
            backend will be used.
        """
        backend = backend or _get_default_backend()
        if backend not in self._backend_adaptors:
            cls = self._get_adaptor_class(backend)
            self._backend_adaptors[backend] = self._create_adaptor(cls)
        return cast("AdaptorType", self._backend_adaptors[backend])

    @property
    def native(self) -> Any:
        """Return the native object of the backend."""
        return self.backend_adaptor()._vis_get_native()

    def _get_adaptor_class(
        self,
        backend: str,
        class_name: str | None = None,
    ) -> Type[AdaptorType]:
        """Retrieves the backend class with the same name as the object class name."""
        if hasattr(self, "BACKEND_ADAPTORS") and backend in self.BACKEND_ADAPTORS:
            adaptor_class = self.BACKEND_ADAPTORS[backend]
            logger.debug(f"Using class-provided adaptor class: {adaptor_class}")
        else:
            class_name = class_name or type(self).__name__
            backend_module = import_module(f"microvis.backend.{backend}")
            adaptor_class = getattr(backend_module, class_name)
        return self.validate_adaptor_class(adaptor_class)

    def _create_adaptor(self, cls: Type[AdaptorType]) -> AdaptorType:
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

        # determine fields that need setter methods in the backend adaptor
        # TODO:
        # this really shouldn't need to be in the init.  `__init_subclass__` would be
        # better, but that unfortunately gets called after EventedModel.__new__.
        # need to look into it
        signals = set(self.__signal_group__._signals_)
        self._evented_fields.update(set(self.__fields__).intersection(signals))

    def _on_any_event(self, info: EmissionInfo) -> None:
        signal_name = info.signal.name
        if not self.has_adaptor or signal_name not in self._evented_fields:
            return

        for adaptor in self._backend_adaptors.values():
            try:
                name = SETTER_METHOD.format(name=signal_name)
                setter = getattr(adaptor, name)
            except AttributeError as e:
                logger.exception(e)
                return

            event_name = f"{type(self).__name__}.{signal_name}"
            logger.debug(f"{event_name}={info.args} emitting to backend")

            try:
                setter(*info.args)
            except Exception as e:
                logger.exception(e)

    # TODO:
    # def detach(self) -> None:
    #     """Disconnect and destroy the backend adaptor from the object."""
    #     self._backend = None

    def validate_adaptor_class(self, adaptor_class: Any) -> type[AdaptorType]:
        """Validate that the adaptor class is appropriate for the core object."""
        # XXX: this could be a classmethod, but it's turning out to be difficult to
        # set _evented_fields on that class (see note in __init__)

        if adaptor_class in self._validated_adaptor_classes:
            return cast("Type[AdaptorType]", adaptor_class)

        cls = type(self)
        logger.debug(f"Validating adaptor class {adaptor_class} for {cls}")
        if missing := {
            SETTER_METHOD.format(name=field)
            for field in self._evented_fields
            if not hasattr(adaptor_class, SETTER_METHOD.format(name=field))
        }:
            raise ValueError(
                f"{adaptor_class} cannot be used as a backend object for "
                f"{cls}: it is missing the following methods: {missing}"
            )
        self._validated_adaptor_classes.add(adaptor_class)
        return cast("Type[AdaptorType]", adaptor_class)


# XXX: the default behavior should be to
# pick the "right" backend for the current environment.  i.e. microvis
# should work with no configuration in both jupyter and ipython desktop.)
def _get_default_backend() -> str:
    """Stub function for the concept of picking a backend when none is specified.

    This will likely be context dependent.
    """
    return "vispy"
