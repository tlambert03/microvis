from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any, Optional, Tuple

from .. import _validators as valid
from .._types import ArrayLike, ValidClim, ValidCmap, ValidColor

if TYPE_CHECKING:
    import numpy as np

from psygnal import EmissionInfo, EventedModel
from psygnal.containers import EventedObjectProxy
from pydantic import Field


class Affine(EventedModel):
    scale: float = Field(default=1.0, ge=0.0)
    translate: float = Field(default=0.0)
    rotate: float = Field(default=0.0)
    shear: float = Field(default=0.0)


class LayerDisplay(EventedModel):
    metadata: dict = Field(default_factory=dict)
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    blending: str = "translucent"
    transform: Affine = Field(default_factory=Affine)


class VolumeDisplay(LayerDisplay):
    interpolation3d: str = "nearest"
    rendering: str = "mip"
    iso_threshold: float = Field(default=0.5, gt=0.0)
    attenuation: float = Field(default=0.05, gt=0.0)


class Image2DDisplay(LayerDisplay):
    cmap: str = "gray"  # TODO
    clim: Optional[Tuple[float, float]] = None  # where none means auto
    gamma: float = 1
    interpolation: str = "nearest"
    visible: bool = True
    name: str = ""


class ImageDisplay(Image2DDisplay, VolumeDisplay):
    ...
    # multiscale=None,
    # cache=True,
    # depiction='volume',
    # plane=None,
    # experimental_clipping_planes=None,


class Image:
    def __init__(self, data: ArrayLike, native: Any):
        self.data = EventedObjectProxy(data)
        self._native = native
        self.display = ImageDisplay()
        self.display.events.connect(self._on_display_change)

    def _on_display_change(self, event: EmissionInfo) -> None:
        v = event.args[0] if len(event.args) == 1 else event.args
        setattr(self._native, event.signal.name, v)

    @property
    def native(self) -> Any:
        return self._native


class ViewBase(abc.ABC):
    # make a protocol rather than an ABC that must be subclassed
    def add_image(
        self,
        data: Any,
        cmap: ValidCmap | None = None,
        clim: ValidClim = "auto",
        **kwargs: Any,
    ) -> Image:
        clim = valid.clim(clim)
        cmap = valid.cmap(cmap)
        node = self._do_add_image(data, cmap=cmap, clim=clim, **kwargs)
        return Image(data, node)

    @abc.abstractmethod
    def _do_add_image(
        self, data: Any, cmap: ValidCmap, clim: ValidClim, **kwargs: Any
    ) -> Image:
        ...


class CanvasBase(abc.ABC):
    def __init__(
        self,
        background_color: str | None = None,
        size: tuple[int, int] = (600, 600),
        **backend_kwargs: Any,
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

    @abc.abstractmethod
    def close(self) -> None:
        ...

    @abc.abstractmethod
    def render(
        self,
        region: tuple[int, int, int, int] | None = None,
        size: tuple[int, int] | None = None,
        bgcolor: ValidColor = None,
        crop: np.ndarray | tuple[int, int, int, int] | None = None,
        alpha: bool = True,
    ) -> np.ndarray:
        """Render to screenshot."""

    # non-abstract methods, optionally override

    @property
    def default_view(self) -> ViewBase:
        return self[0, 0]

    def __enter__(self) -> CanvasBase:
        self.show()
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
