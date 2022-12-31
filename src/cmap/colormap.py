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
    Sequence,
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
        """Return a pygfx TextureView, or Texture if as_view is False.

        If you want to customize the TextureView, use `as_view == False` and then
        call `get_view()` on the returned Texture, providing the desired arguments.
        """
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

    def to_altair(self) -> list[tuple[float, str]]:
        """Return an altair colorscale."""
        return [(x.position, x.color.hex) for x in self.stops]

    def iter_colors(self, N: Iterable[int] | int = 256) -> Iterator[Color]:
        """Return a list of N colors sampled over the range of the colormap.

        If N is an integer, it will return a list of N colors spanning the full range
        of the colormap. If N is an iterable, it will return a list of colors at the
        positions specified by the iterable.
        """
        nums = np.linspace(0, 1, N) if isinstance(N, int) else np.asarray(N)
        for c in self(nums):
            yield Color(c)

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable]:
        yield cls._validate  # pydantic validator  # pragma: no cover

    @classmethod
    def _validate(cls, v: Any) -> LinearColormap:
        if isinstance(v, cls):
            return v
        if isinstance(v, str):
            if v.endswith("_r"):
                return cls([v[:-2], None], id=v)
            return cls([None, v], id=v)
        return cls(v)


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


class Colormap:
    def __init__(self, colors: Any) -> None:
        self._stops = ColorStops.parse(colors)


class ColorStop(NamedTuple):
    """A color stop in a color gradient."""

    position: float
    color: Color


class ColorStops(Sequence[ColorStop]):
    """A sequence of color stops in a color gradient.

    Convenience class allowing various operations on a sequence of color stops,
    including casting to an (N, 5) array (e.g. `np.asarray(ColorStops(...))`)
    """

    _stops: np.ndarray  # internally, stored as an (N, 5) array

    @classmethod
    def parse(
        cls,
        colors: str | Iterable[Any],
        fill_mode: Literal["neighboring", "fractional"] = "neighboring",
    ) -> ColorStops:
        """Parse `colors` into a sequence of color stops.

        This is the more flexible constructor.t

        Each item in `colors` can be a color, or a 2-tuple of (position, color), where
        position (the "stop" along a color gradient) is a float between 0 and 1.  Where
        not provided, color positions will be evenly distributed between neighboring
        specified positions (if `fill_mode` is 'neighboring') or will be replaced with
        `index / (len(colors)-1)` (if `fill_mode` is 'fractional').

        Colors can be expressed as anything that can be converted to a Color, including
        a string, or 3/4-sequence of RGB(A) values.

        Parameters
        ----------
        colors : str | Iterable[Any]
            Colors and (optional) stop positions.
        fill_mode : {'neighboring', 'fractional'}, optional
            How to fill in missing stop positions.  If 'neighboring' (the default),
            missing positions will be evenly distributed between the closest specified
            neighboring positions.  If 'fractional', missing stop positions will be
            replaced with `index / (len(colors)-1)`.  For example:

            >>> s = ColorStops.parse(['r', 'y', (0.8,'g'), 'b'])
            >>> s.stops
            # 'y' is halfway between 'r' and 'g'
            (0.0, 0.4, 0.8, 1.0)
            >>> s = ColorStops.parse(['r', 'y', (0.8,'g'), 'b'], fill_mode='fractional')
            >>> s.stops
            # 'y' is 1/3 of the way between 0 and 1
            (0.0, 0.3333333333333333, 0.8, 1.0)

        Returns
        -------
        ColorStops
            A sequence of color stops.
        """
        if fill_mode not in {"neighboring", "fractional"}:
            raise ValueError(
                f"fill_mode must be 'neighboring' or 'fractional', not {fill_mode!r}"
            )

        colors = [None, colors] if isinstance(colors, str) else list(colors)
        if len(colors) == 1:
            colors = [None, colors[0]]

        _positions: list[float | None] = []
        _colors: list[Color] = []
        for item in colors:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                # a 2-tuple cannot be a valid color, so it must be a stop
                _position, item = item
            elif (isinstance(item, (list, tuple)) and len(item) == 5) or (
                isinstance(item, np.ndarray) and item.shape == (5,)
            ):
                _position, *item = item
            else:
                _position = None
            _positions.append(_position)
            _colors.append(Color(item))  # this will raise if invalid

        if fill_mode == "fractional":
            N = len(_positions) - 1
            _stops = [n / N if i is None else i for n, i in enumerate(_positions)]
        else:
            _stops = _fill_stops(_positions)

        return ColorStops(zip(_stops, _colors))

    def __init__(self, stops: np.ndarray | Iterable[tuple[float, Color]]) -> None:
        if isinstance(stops, np.ndarray):
            if stops.shape[1] != 5:
                raise ValueError("Expected (N, 5) array")
            self._stops = stops
        else:
            self._stops = np.array([(p,) + tuple(c) for p, c in stops])

    @property
    def stops(self) -> tuple[float, ...]:
        """Return the positions of the color stops."""
        return tuple(self._stops[:, 0])

    @property
    def colors(self) -> tuple[Color, ...]:
        """Return all colors in this object."""
        return tuple(Color(c) for c in self._stops[:, 1:])

    def __len__(self) -> int:
        return len(self._stops)

    @overload
    def __getitem__(self, key: int) -> ColorStop:
        ...

    @overload
    def __getitem__(self, key: slice) -> ColorStops:
        ...

    @overload
    def __getitem__(self, key: tuple) -> np.ndarray:
        ...

    def __getitem__(
        self, key: int | slice | tuple
    ) -> ColorStop | ColorStops | np.ndarray:
        """Get an item or slice of the color stops.

        If key is an integer, return a single `ColorStop` tuple.
        If key is a slice, return a new `ColorStops` object.
        If key is a tuple, return a numpy array (standard numpy indexing).
        """
        # sourcery skip: assign-if-exp, reintroduce-else
        if isinstance(key, slice):
            return ColorStops(self._stops[key])
        if isinstance(key, tuple):
            return np.asarray(self)[key]  # type: ignore
        pos, *rgba = self._stops[key]
        return ColorStop(pos, Color(rgba))

    def __array__(self) -> np.ndarray:
        """Return (N, 5) array, N rows of (position, r, g, b, a)."""
        return self._stops

    def __repr__(self) -> str:
        m = ",\n  ".join(repr((pos, Color(rgba))) for pos, *rgba in self._stops)
        return f"ColorStops(\n  {m}\n)"

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable]:
        yield cls.parse  # pydantic validator  # pragma: no cover

    def to_lut(self, N: int = 256, gamma: float = 1.0) -> np.ndarray:
        """Create (N, 4) LUT of RGBA values, interpolated between color stops."""
        return _colorstops_to_lut(N, self, gamma)


def _fill_stops(stops: Iterable[float | None]) -> list[float]:
    """Fill in missing stop positions.

    Replace None values in the list of stop positions with values spaced evenly
    between the nearest non-`None` values.

    Parameters
    ----------
    stops : list[float | None]
        List of stop positions.

    Examples
    --------
    >>> fill_stops([0.0, None, 0.5, None, 1.0])
    [0.0, 0.25, 0.5, 0.75, 1.0]
    >>> fill_stops([None, None, None])
    [0.0, 0.5, 1.0]
    >>> fill_stops([None, None, 0.8, None, 1.0])
    [0.0, 0.4, 0.8, 0.9, 1.0]
    """
    _stops = list(stops)
    if not _stops:
        return []

    # make edges 0-1 unless they are explicitly set
    if _stops[0] is None:
        _stops[0] = 0.0
    if _stops[-1] is None:
        _stops[-1] = 1.0

    out: list[float] = []
    last_val: tuple[int, float] = (0, 0.0)
    in_gap = False  # marks whether we are in a series of Nones
    for idx, stop in enumerate(_stops):
        if stop is not None:
            if in_gap:
                # if we are at the first value after a series of Nones, then
                # fill in the Nones with values spaced evenly between the
                # previous value and the current value.
                _idx, _stop = last_val
                filler = np.linspace(_stop, stop, idx - _idx + 1)
                out.extend(filler[1:])
                in_gap = False
            else:
                # otherwise, just append the current value
                out.append(stop)
            last_val = (idx, stop)
        else:
            in_gap = True
    return out


def _colorstops_to_lut(N: int, data: ArrayLike, gamma: float = 1.0) -> np.ndarray:
    """Convert an (M, 5) array of (position, r, g, b, a) values to an (N, 4) LUT.

    The output array will have N rows, and 4 columns (r, g, b, a). Each row represents
    the color at an evenly spaced position along the color gradient, from 0 to 1.

    This array can be used to create a color map, or to apply a color gradient to data
    that has been normalized to the range 0-1. (e.g. lut.take(data * (N-1), axis=0))


    Parameters
    ----------
    N : int
        Number of interpolated values to generate in the output LUT.
    data : ArrayLike
        Array of (position, r, g, b, a) values.
    gamma : float, optional
        Gamma correction to apply to the output LUT, by default 1.0

    Returns
    -------
    lut : np.ndarray
        (N, 4) LUT of RGBA values, interpolated between color stops.
    """
    adata = np.array(data)
    if adata.ndim != 2 or adata.shape[1] != 5:
        raise ValueError("data must have 2 columns")

    # make sure the first and last stops are at 0 and 1 ...
    # adding additional control points that copy the first/last color if needed
    if adata[0, 0] != 0.0:
        adata = np.vstack([[0.0, *adata[0, 1:]], adata])
    if adata[-1, 0] != 1.0:
        adata = np.vstack([adata, [1.0, *adata[-1, 1:]]])

    x = adata[:, 0]
    rgba = adata[:, 1:]

    if (np.diff(x) < 0).any():
        raise ValueError("Color stops must be in ascending position order")

    # begin generation of lookup table
    if N == 1:
        # convention: use the y = f(x=1) value for a 1-element lookup table
        lut = rgba[-1]
    else:
        # sourcery skip: extract-method
        # scale stop positions to the number of elements (-1) in the LUT
        x = x * (N - 1)
        # create evenly spaced LUT indices with gamma correction
        xind = np.linspace(0, 1, N) ** gamma
        # scale to the number of elements (-1) in the LUT, and exclude exterior values
        xind = ((N - 1) * xind)[1:-1]
        # Find the indices in the scaled positions array `x` that each element in
        # `xind` would need to be inserted before to maintain order.
        ind = np.searchsorted(x, xind)
        # calculate the fractional distance between the two values in `x` that
        # each element in `xind` is between. (this is the position at which we need
        # to sample between the neighboring color stops)
        frac_dist = (xind - x[ind - 1]) / (x[ind] - x[ind - 1])
        # calculate the color at each position in `xind` by linearly interpolating
        # the value at `frac_dist` between the neighboring color stops
        start = rgba[ind - 1]
        length = rgba[ind] - start
        interpolated_points = frac_dist[:, np.newaxis] * length + start
        # concatenate the first and last color stops with the interpolated values
        lut = np.concatenate([[rgba[0]], interpolated_points, [rgba[-1]]])

    # ensure that the lut is confined to values between 0 and 1 by clipping it
    return np.clip(lut, 0.0, 1.0)  # type: ignore
