from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    Iterator,
    Literal,
    NamedTuple,
    Protocol,
    overload,
)

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .color import Color

if TYPE_CHECKING:
    import pygfx
    from bokeh.models import LinearColorMapper as BokehLinearColorMapper
    from matplotlib.colors import LinearSegmentedColormap as MplLinearSegmentedColormap
    from napari.utils.colormaps import Colormap as NapariColormap
    from vispy.color import Colormap as VispyColormap

    from .color import ValidColor


class PColorMapper(Protocol):
    @overload
    def __call__(self, X: float) -> Color:
        ...

    @overload
    def __call__(self, X: NDArray) -> NDArray[np.float64]:
        ...

    def __call__(self, X: float | ArrayLike) -> Color | NDArray[np.float64]:
        """Map a scalar or array of scalars to RGBA colors.

        Parameters
        ----------
        X : float or ndarray
            The data value(s) to convert to RGBA.
            X should be in the interval `[0.0, 1.0]` to
            return the RGBA values `X*100` percent along the Colormap line.

        Returns
        -------
        Tuple of (R,G,B,A) values if X is scalar, otherwise an array of
        RGBA values with a shape of `X.shape + (4, )`.
        """


class Colormap:
    _luts: dict[int, np.ndarray]
    _stops: tuple[ColorStop, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "_luts", {})  # because frozen=True

    def __call__(self, X: float | ArrayLike) -> Color | NDArray[np.float64]:
        lut = self.lut()
        xa = np.array(X, copy=True)
        if not xa.dtype.isnative:
            xa = xa.byteswap().newbyteorder()  # Native byteorder is faster.
        if xa.dtype.kind == "f":
            N = len(lut)
            with np.errstate(invalid="ignore"):
                xa *= N
                # Negative values are out of range, but astype(int) would
                # truncate them towards zero.
                xa[xa < 0] = -1
                # xa == 1 (== N after multiplication) is not out of range.
                xa[xa == N] = N - 1
                # Avoid converting large positive values to negative integers.
                np.clip(xa, -1, N, out=xa)
                xa = xa.astype(int)

        result = lut.take(xa, axis=0, mode="clip")
        return result if np.iterable(X) else Color(result)

    def lut(self, n: int = 256) -> np.ndarray:
        if n not in self._luts:
            self._luts[n] = self._make_lut(n)
        return self._luts[n]

    def _make_lut(self, n: int) -> np.ndarray:
        raise NotImplementedError

    def __rich_repr__(self) -> Any:
        from rich import get_console
        from rich.style import Style
        from rich.text import Text

        console = get_console()
        color_cell = Text("")
        X = np.linspace(0, 1.0, console.width - 12, dtype=np.float64)
        for _color in self(X):
            color_cell += Text(" ", style=Style(bgcolor=Color(_color).hex[:7]))
        console.print(color_cell)


class ColorStop(NamedTuple):
    """A color stop in a color gradient."""

    position: float
    color: Color


@dataclass(frozen=True)
class LinearColormap(Colormap):
    """Linearly interpolated colormap."""

    colors: list[ValidColor | ColorStop | tuple[float, ValidColor]] = field(
        compare=False
    )
    id: str | None = None
    display_name: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if len(self.colors) < 1:
            raise ValueError("LinearColormap must have at least 1 color")
        colors = self.colors
        if len(colors) == 1:
            colors = [Color(None), colors[0]]

        # create a list of ColorStop from the input
        nsteps: int = len(colors) - 1
        _stops: list[ColorStop] = []
        for i, color in enumerate(colors):
            if isinstance(color, ColorStop):
                _stops.append(color)
            elif isinstance(color, tuple) and len(color) == 2:
                # a 2-tuple cannot be a valid color, so it must be a stop
                _stops.append(ColorStop(color[0], Color(color[1])))
            else:
                _stops.append(ColorStop(i / nsteps, Color(color)))

        if _stops[0].position != 0.0:
            _stops.insert(0, ColorStop(0.0, _stops[0].color))
        if _stops[-1].position != 1.0:
            _stops.append(ColorStop(1.0, _stops[-1].color))

        object.__setattr__(self, "_stops", tuple(_stops))

    @property
    def stops(self) -> tuple[ColorStop, ...]:
        """Return list of normalized stops."""
        return self._stops

    def _make_lut(self, N: int = 256) -> np.ndarray:
        """Return (N, 4) lookup table for this colormap.

        This creates a lookup table with N steps, linearly interpolating between each
        color stop in the colormap.
        """
        lut = np.ones((N, 4), float)
        stops, colors = zip(*self.stops)
        r, g, b, a = np.array([tuple(x) for x in colors]).T
        lut[:, 0] = _create_lookup_table(N, np.array([stops, r, r]).T)
        lut[:, 1] = _create_lookup_table(N, np.array([stops, g, g]).T)
        lut[:, 2] = _create_lookup_table(N, np.array([stops, b, b]).T)
        lut[:, 3] = _create_lookup_table(N, np.array([stops, a, a]).T)
        return lut

    def to_mpl(self, N: int = 256) -> MplLinearSegmentedColormap:
        """Return a matplotlib colormap."""
        import matplotlib.colors as mplc

        return mplc.LinearSegmentedColormap.from_list(self.id, self.stops, N=N)

    def to_vispy(self) -> VispyColormap:
        """Return a vispy colormap."""
        from vispy.color import Colormap

        controls, colors = zip(*self.stops)
        return Colormap(colors=[tuple(x) for x in colors], controls=controls)

    @overload
    def to_pygfx(
        self, N: int = ..., *, as_view: Literal[True] = ...
    ) -> pygfx.TextureView:
        ...

    @overload
    def to_pygfx(self, N: int = ..., *, as_view: Literal[False]) -> pygfx.Texture:
        ...

    def to_pygfx(
        self, N: int = 256, *, as_view: bool = True
    ) -> pygfx.TextureView | pygfx.Texture:
        """Return a pygfx texture."""
        import pygfx

        colors = self.iter_colors(N)
        colormap_data = np.array([tuple(c) for c in colors], dtype=np.float32)
        tex = pygfx.Texture(colormap_data, dim=1)
        return tex.get_view() if as_view else tex

    def to_plotly(self) -> list[list[float | str]]:
        """Return a plotly colorscale."""
        return [[s, c.hex] for s, c in self.stops]

    def to_napari(self) -> NapariColormap:
        """Return a napari colormap."""
        from napari.utils.colormaps import Colormap

        controls, colors = zip(*self.stops)
        return Colormap(
            colors=[tuple(x) for x in colors],
            controls=controls,
            name=self.id or "custom colormap",
            display_name=self.display_name,
        )

    def to_bokeh(self, N: int = 256) -> BokehLinearColorMapper:
        """Return a bokeh colorscale."""
        from bokeh.models import LinearColorMapper

        return LinearColorMapper([c.hex for c in self.iter_colors(N)])

    def iter_colors(self, N: Iterable[int] | int = 256) -> Iterator[Color]:
        """Return a list of N colors sampled over the range of the colormap.

        If N is an integer, it will return a list of N colors spanning the full range
        of the colormap. If N is an iterable, it will return a list of colors at the
        positions specified by the iterable.
        """
        nums = np.linspace(0, 1, N) if isinstance(N, int) else np.asarray(N)
        for c in self(nums):
            yield Color(c)

    def to_altair(self) -> list[tuple[float, str]]:
        """Return an altair colorscale."""
        return [(x.position, x.color.hex) for x in self.stops]

    # def to_vtk(self) -> vtkLookupTable:
    #     """Return a vtkLookupTable."""
    #     import vtk

    #     lut = vtkLookupTable()
    #     lut.SetNumberOfTableValues(N)
    #     lut.Build()
    #     for i, color in enumerate(self(N)):
    #         lut.SetTableValue(i, *color)
    #     return lut

    # def to_pyvista(self, N: int = 256) -> pyvista.LookupTable:
    #     """Return a pyvista LookupTable."""
    #     lut = pyvista.LookupTable()
    #     lut.SetNumberOfTableValues(N)
    #     lut.Build()
    #     for i, color in enumerate(self(N)):
    #         lut.SetTableValue(i, *color)
    #     return lut

    # def to_pythreejs(self, N: int = 256) -> list[float]:
    #     """Return a pythreejs colormap."""
    #     return [x for x in self(N).ravel()]

    # def to_pydeck(self, N: int = 256) -> list[tuple[float, str]]:
    #     """Return a pydeck colorscale."""
    #     return [(x.position, x.color.hex) for x in self.stops]

    # def to_cmapy(self, N: int = 256) -> Cmap:
    #     """Return a cmapy colormap."""
    #     return Cmap([(x.position, x.color.hex) for x in self.stops])

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable]:
        yield cls.validate  # pydantic validator  # pragma: no cover

    @classmethod
    def validate(cls, value: Any) -> LinearColormap:
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            if value.endswith("_r"):
                return cls([value[:-2], None], id=value)
            return cls([None, value], id=value)
        return cls(value)


def _create_lookup_table(N: int, data: np.ndarray, gamma: float = 1.0) -> np.ndarray:
    try:
        adata = np.array(data)
    except ValueError as err:
        raise TypeError("data must be convertible to an array") from err
    # _api.check_shape((None, 3), data=adata)

    x = adata[:, 0]
    y0 = adata[:, 1]
    y1 = adata[:, 2]

    if x[0] != 0.0 or x[-1] != 1.0:
        raise ValueError("data mapping points must start with x=0 and end with x=1")
    if (np.diff(x) < 0).any():
        raise ValueError("data mapping points must have x in increasing order")
    # begin generation of lookup table
    if N == 1:
        # convention: use the y = f(x=1) value for a 1-element lookup table
        lut = np.array(y0[-1])
    else:
        x = x * (N - 1)
        xind = (N - 1) * np.linspace(0, 1, N) ** gamma
        ind = np.searchsorted(x, xind)[1:-1]

        distance = (xind[1:-1] - x[ind - 1]) / (x[ind] - x[ind - 1])
        lut = np.concatenate(
            [
                [y1[0]],
                distance * (y0[ind] - y1[ind - 1]) + y1[ind - 1],
                [y0[-1]],
            ]
        )
    # ensure that the lut is confined to values between 0 and 1 by clipping it
    return np.clip(lut, 0.0, 1.0)
