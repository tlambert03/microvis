from __future__ import annotations

from abc import abstractmethod
from typing import Any, ClassVar, Protocol, TypeVar, cast

from psygnal import EmissionInfo
from psygnal.containers import EventedObjectProxy
from pydantic import PrivateAttr
from pydantic.generics import GenericModel

from ..._types import ArrayLike
from .node import Node, NodeBackend, NodeType


class DataNodeBackend(NodeBackend[NodeType], Protocol):
    """Protocol for a backend DataNode adapter object."""

    @abstractmethod
    def _viz_set_data(self, arg: ArrayLike) -> None:
        ...


DataNodeBackendT = TypeVar("DataNodeBackendT", bound=DataNodeBackend, covariant=True)


class DataField(GenericModel):
    def apply(self, data: ArrayLike) -> Any:
        return self


class DataNode(Node[DataNodeBackendT]):
    """A node that has data.

    Data is wrapped in an evented object proxy so that mutation events can be seen.
    """

    _BackendProtocol: ClassVar[type] = DataNodeBackend
    _data: EventedObjectProxy[ArrayLike] = PrivateAttr(None)

    def __init__(self, data: ArrayLike, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.data = cast("EventedObjectProxy", data)

    @property
    def data(self) -> EventedObjectProxy[ArrayLike]:
        """Return data, wrapped with a proxy that notifies on data mutation."""
        return self._data

    @data.setter
    def data(self, data: ArrayLike) -> None:
        if self._data is not None:
            self._data.events.disconnect(self._on_data_changed)
        if isinstance(data, EventedObjectProxy):
            self._data = data  # don't rewrap
        else:
            self._data = EventedObjectProxy(data)
        self._on_data_changed()
        self._data.events.connect(self._on_data_changed)

    def _on_data_changed(self) -> None:
        # Note: could accept an EmissionInfo argument here and gate the
        # update on event types.
        if self.has_backend:
            self.backend_adaptor()._viz_set_data(self.data_raw)

    @property
    def data_raw(self) -> ArrayLike | None:
        """Return data, without the proxy."""
        if self._data is None:
            return None
        return cast("ArrayLike", self._data.__wrapped__)

    def _on_any_event(self, info: EmissionInfo) -> None:
        if not self.has_backend:
            return

        # if the event is coming from a DataField, make
        # sure to apply the data to the field before emitting to the backend
        # ... TODO: this is subject to change
        signal_name = info.signal.name
        obj = getattr(self, signal_name)
        if isinstance(obj, DataField):
            val = obj.apply(self.data_raw)
            info = EmissionInfo(info.signal, (val,))

        super()._on_any_event(info)
