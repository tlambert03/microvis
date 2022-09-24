from psygnal.containers import EventedObjectProxy
from psygnal import EmissionInfo
from .._types import ArrayLike
from ..schema import ImageDisplay
from .._protocols import FrontEndFor, ImageBackend


class Image(FrontEndFor[ImageBackend], ImageDisplay):
    def __init__(self, data: ArrayLike):
        self.data: EventedObjectProxy[ArrayLike] = EventedObjectProxy(data)
