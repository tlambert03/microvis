from __future__ import annotations

from abc import abstractmethod
from typing import Any, Protocol, TypeVar, cast

from psygnal import EmissionInfo
from psygnal.containers import EventedObjectProxy
from pydantic import PrivateAttr
from pydantic.generics import GenericModel

from microvis._types import ArrayLike

from .node import Node, NodeAdaptorProtocol, NodeTypeCoV


class DataNodeAdaptorProtocol(NodeAdaptorProtocol[NodeTypeCoV], Protocol):
    """Protocol for a backend DataNode adaptor object."""

    @abstractmethod
    def _vis_set_data(self, arg: ArrayLike) -> None:
        ...


DataNodeBackendT = TypeVar(
    "DataNodeBackendT", bound=DataNodeAdaptorProtocol, covariant=True
)


class DataField(GenericModel):
    def apply(self, data: ArrayLike) -> Any:
        return self


# TODO: make the ArrayLike here a generic type parameter on DataNode


class DataNode(Node[DataNodeBackendT]):
    """A node that has data.

    Data is wrapped in an evented object proxy so that mutation events can be seen.
    """

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
            # disconnect the old wrapper
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
        if self.has_adaptor():
            self.backend_adaptor()._vis_set_data(cast(ArrayLike, self.data_raw))

    @property
    def data_raw(self) -> ArrayLike | None:
        """Return data, without the proxy."""
        if self._data is None:
            return None
        return cast("ArrayLike", self._data.__wrapped__)

    def _on_any_event(self, info: EmissionInfo) -> None:
        if not self.has_adaptor():
            return

        # if the event is coming from a DataField, make
        # sure to apply the data to the field before emitting to the backend
        # ... TODO: this is subject to change
        signal_name = info.signal.name
        obj = getattr(self, signal_name)
        if isinstance(obj, DataField) and self._data is not None:
            val = obj.apply(cast(ArrayLike, self.data_raw))
            info = EmissionInfo(info.signal, (val,))

        super()._on_any_event(info)
