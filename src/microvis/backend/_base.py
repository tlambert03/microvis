import abc
from typing import Any
from .._types import ValidCmap, ValidClim


class Image:
    ...


class ViewBase(abc.ABC):
    @abc.abstractmethod
    def add_image(
        self, data: Any, cmap: ValidCmap, clim: ValidClim, **kwargs: Any
    ) -> Image:
        ...


class CanvasBase(abc.ABC):
    def __init__(
        self,
        background_color: str | None = None,
        size: tuple[int, int] = (600, 600),
        show: bool = False,
        **kwargs: Any,
    ) -> None:
        ...

    @abc.abstractmethod
    def native(self) -> Any:
        ...

    @abc.abstractmethod
    def __getitem__(self, idxs: tuple[int, int]) -> ViewBase:
        ...

    @abc.abstractmethod
    def __delitem__(self, idxs: tuple[int, int]) -> None:
        ...

    @abc.abstractmethod
    def show(self) -> None:
        ...

    @property
    def default_view(self) -> ViewBase:
        return self[0, 0]
