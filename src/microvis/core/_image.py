from psygnal.containers import EventedObjectProxy
from psygnal import EmissionInfo
from .._types import ArrayLike
from ..schema import ImageNode
from .._protocols import FrontEndFor, ImageBackend
from pydantic import PrivateAttr


class Image(FrontEndFor[ImageBackend]):
    def __init__(self, data=None, **kwargs):
        self.data = data
        super().__init__()
        self._display = ImageNode(**kwargs)

    @property
    def data(self) -> EventedObjectProxy[ArrayLike]:
        return self._data

    @property
    def display(self) -> ImageNode:
        return self._display

    @data.setter
    def data(self, data: ArrayLike) -> None:
        self._data = EventedObjectProxy(data)

    def _on_any_event(self, info: EmissionInfo) -> None:
        if info.signal.name == "data":
            self._backend._viz_set_data(*info.args)
        else:
            super()._on_any_event(info)

    class Config:
        allow_property_setters = True
