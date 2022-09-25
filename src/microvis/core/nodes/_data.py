from psygnal.containers import EventedObjectProxy
from pydantic import PrivateAttr
from typing import Any
from .node import Node
from ..._types import ArrayLike


class DataNode(Node):
    """A node that has data.

    Data is wrapped in an evented object proxy so that mutation events can be seen.
    """

    _data: EventedObjectProxy[ArrayLike] = PrivateAttr()

    def __init__(self, data: ArrayLike, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._data = EventedObjectProxy(data)  # type: ignore

    @property
    def data(self) -> EventedObjectProxy[ArrayLike]:
        """Return data, wrapped with a proxy that notifies on data mutation."""
        return self._data

    @data.setter
    def data(self, data: ArrayLike) -> None:
        if isinstance(data, EventedObjectProxy):
            data = data.__wrapped__  # don't rewrap
        self._data = EventedObjectProxy(data)

    @property
    def data_raw(self) -> ArrayLike:
        """Return data, without the proxy."""
        return self._data.__wrapped__  # type: ignore
