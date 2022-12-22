# slicing data - thoughts

## Spaces
- rendering space (2D/3D)
- nagivable nD space (nD)

If we can separate concerns over these things and still allow for 
reshuffling dims and computing dynamic projections then we're onto a winner

## Data Model
We need to be explicit about different kinds of data, our full nD data and 
the visualisable 2D/3D data which will be rendered

### nD Data
this is arbitrary nD array data
`data: ArrayLike[...]`

This data will be transformed into one of the following for slicing
- `dense_data: ArrayLike['... rgb(a) proj d h w']`
- `coordinate_data: ArrayLike['... n coords']`

### Renderable Data
- `renderable_dense_data: ArrayLike['rgb(a) proj d h w']`
- `renderable_coordinate_data: ArrayLike['n (2|3)']'`

### Separating nD into navigable + renderable 2/3D

Let's take a look at how we would map nD data into renderable data through 
some examples for both dense data and coordinate data

We won't look at the mechanics/how to generalise/implement this yet, just 
specify the mapping

#### Dense Data

##### time series of 2D intensity images
- data shape: `(t h w)`
- navigable dimensions in 2D: `(t)`
- navigable dimensions in 3D: `(t)`
- renderable data shape: `(1 1 1 h w)`

##### time series of 2D RGB(A) images
- data shape: `(t h w c)`
- navigable dimensions in 2D: `(t)`
- navigable dimensions in 3D: `(t)`

##### time series of 2D intensity images with local projections
- data shape: `(t h w)`
- navigable dimensions in 2D: `(t)`
- navigable dimensions in 3D: `(t)`
- renderable data shape: `(1 proj 1 h w)`

We create a [sliding window view](https://numpy.org/devdocs/reference/generated/numpy.lib.stride_tricks.sliding_window_view.html)
for the window of time we want to project and put that in the channel dimension.

Prior to rendering, the 'proj' dimension is 'projected' according to some 
arbitrary reduction function on the CPU. Keeping 'rgb(a)' separate from 'proj' 
allows the model to be used to compute dynamic projections from RGB data.

##### time series of 3D intensity images
- data shape: `(t d h w)`
- navigable dimensions in 2D: `(t d)`
- navigable dimensions in 3D: `(d)`
- renderable data shape: `(1 1 d h w)`

##### crazy multiplexed multichannel 3D time-lapse with local projections
- data shape: `(t m c d h w)`
- navigable dimensions in 2D: `(t m c d)`
- navigable dimensions in 3D: `(t m c)`
- renderable data shape: `(1 proj d h w)`

again, take a sliding window over time to yield the proj dimension then 
reduce on CPU before passing to renderer

As in napari - multichannel 3D should be navigable, but to render correctly 
you should have each channel as an independent image

maybe we have multichannelimage as a separate thing to make this easy for people

#### Coordinate Data

note: at the minute we don't have any 'projection' dimension for coordinate 
data but we definitely could, not 100% on the use cases though.

##### 2D coordinates
- data shape: `(n d)` `d=2`
- navigable dimensions in 2D: `()`
- navigable dimensions in 3D: `()`
- renderable data shape: `(n 2)`

Simple. 
When viewing in 3D, 2D coordinates are (optionally) broadcast over the third 
dim.

##### 3D coordinates
- data shape: `(n d)` `d=3`
- navigable dimensions in 2D: `(d=0)`
- navigable dimensions in 3D: `()`
- renderable data shape 2D: `(n 3)`

Same as napari.

##### nD coordinates
- data shape: `(n d)` `d=5`
- navigable dimensions in 2D: `(d=0 d=1 d=2)` (`d[:-2]`)
- navigable dimensions in 3D: `(d=0 d=1)` (`d[:-3]`)
- renderable data shape 2D: `(n 2)` (2 = d[-2:] = d[3], d[4])
- renderable data shape 3D: `(n, 3)` (3 = d[-3:] = d[2], d[3], d[4])

Same as napari.

##### nD coordinate time series (stacked)
stacked nd coordinates

- data shape: `(t n d)` `(d=5)
- navigable dimensions in 2D: `(t d=0 d=1 d=2)` (`t d[:-2]`)
- navigable dimensions in 3D: `(t d=0 d=1)` (`t d[:-3]`)

not possible in napari

replace `t` with `...` to generalise from simple stack to nD stack of nD coords.

### World models

This yields two separate world models, tentatively the 'navigable world' and 
the 'scene' which can be rendered from the `renderable_data` for both
dense data and coordinate data.

```python
class Scene:
    ndim: Literal[2, 3]

class World:
    ndim: int # computed from number of navigable dimensions of each node
    position: Tuple[int, ...] # position in nD 'navigable world', len == ndim
```
