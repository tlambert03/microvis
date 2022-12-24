# slicing data - thoughts

## Spaces
- renderable space (2D/3D)
- nagivable nD space (nD)

If we can separate concerns over these things and still allow for 
reshuffling dims and computing dynamic projections then we're onto a winner

The renderable space is what we can actually see at any one time. The 
navigable space is the rest of the full nD space of the data in the scene. 
You can imagine having sliders to navigate the navigable space like in napari.

The main difference between this model and napari is the explicit separation 
of these two 'spaces', napari treats everything as one unified nD coordinate 
system.

## TL;DR

- images: nD Data --[slicing]-->  Renderable Data  --[reduction]--> 2D/3D 
- coordinates: nD data --[slicing]--> Renderable Data

## Data Model
We need to be explicit about different types of data we deal with
- the full nD data we accept
- the data we can actually render in given ways


### nD Data
this is arbitrary nD array data
`data: ArrayLike[...]`

This data will be transformed into one of the following prior to 'slicing' 
for visualisation.
- `dense_data: ArrayLike['... rgb(a) 1 d h w']`
- `coordinate_data: ArrayLike['... n coords']`

Note: the dimension of length 1 in this data model is an axis over which an 
arbitrary reduction will be performed before data is passed to the rendering 
engine. This is a (useful) depature which allows us to model local projections 
over windows of time/space during slicing. Slicing over a windowed region  
will yield a dimension of the same length as the window whilst point 
slicing will yield a dimension of length 1.

### Renderable Data

This is the data we get by slicing promise to eventually render in both 2D 
and 3D.

- dense gridded data: `ArrayLike['rgb(a) proj d h w']`
- coordinate data: `ArrayLike['n (2|3)']'`



### Slicing: Separating nD into navigable dims + renderable dims

Let's take a look at how we would think about doing slicing for various types 
of nD data through some examples.

To do this, we need to separate the data dimensions into our two spaces, the 
navigable nD space (over which we might have sliders defining a point/region 
a la napari) and the rendered space, which dimensions are we actually 
visualising at any one time.

We won't look at the mechanics/how to implement this yet, just 
specify the mapping from nD to our two spaces.

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
- renderable data shape: `(c 1 1 h w)`

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

Coordinate data should be able to be nD and arbitrarily stacked.

note: at the minute we don't have any 'projection' dimension for coordinate 
data but we definitely could...

##### 2D coordinates
- data shape: `(n coord)` `coord=2`
- navigable dimensions in 2D: `()`
- navigable dimensions in 3D: `()`
- renderable data shape: `(n coord)`

Simple. 
When viewing in 3D, 2D coordinates are (optionally) broadcast over the third 
dim.

These index into our 3D space following broadcasting rules:
`(d h w) == (1 coord[0] coord[1])`

two coordinate dimensions are aligned with `d h w` to the right then 
prepended with ones.

##### 3D coordinates
- data shape: `(n coord)` `coord=3`
- navigable dimensions in 2D: `(coord=0)`
- navigable dimensions in 3D: `()`
- renderable data shape 2D: `(n 3)`

Same as napari.

These index into our 3D space following broadcasting rules:
`(d h w) == (coord[0] coord[1] coord[2])`

three coordinate dimensions are already aligned with `d h w`.

##### nD coordinates
- data shape: `(n d)` `d=5`
- navigable dimensions in 2D: `(d=0 d=1 d=2)` (`d[:-2]`)
- navigable dimensions in 3D: `(d=0 d=1)` (`d[:-3]`)
- renderable data shape 2D: `(n 2)` (2 = d[-2:] = d[3], d[4])
- renderable data shape 3D: `(n 3)` (3 = d[-3:] = d[2], d[3], d[4])

Same as napari.

##### nD coordinate time series (stacked)
stacked nd coordinates

- data shape: `(n t d)` `(d=5)
- navigable dimensions in 2D: `(t d=0 d=1 d=2)` (`t d[:-2]`)
- navigable dimensions in 3D: `(t d=0 d=1)` (`t d[:-3]`)

not possible in napari

replace `t` with `...` to generalise from simple 1D stack to nD stack of nD 
coords.

#### Unified example

Let's say we have a 2D image stack and a stack of 2D coordinates
- image: `t h w`
- per-image coordinates: `n t yx` (`yx=2`)

We map them both into the (navigable world) and (rendered scene) spaces
- `t h w -> (t) (1 1 1 h w)`
- `n t yx -> (t) n*(1 1 1 y x)`

This is cool! and hard to do with the napari dims model because of the `(n, 
d)` requirement.

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
