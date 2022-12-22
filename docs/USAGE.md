# Code Organization and Usage

temporary docs for usage, and explanation of code organization for developers.  See also the [CONTRIBUTING](../CONTRIBUTING.md) guide,
which outlines a lot of design principles that we're aiming for here.

## Code Organization

### `convenience`

The convenience module (to be renamed), is where high-level, "user-facing" APIs
are defined.  These are the functions that end-users should be encouraged to use
(such as `imshow`, etc...).  These functions build on `core`.

### `core`

The core module is where most of the microvis logic is defined.  This is where
all of the scene-graph model abstractions are defined.  Currently, this
includes:

- **`core.Canvas`**: The canvas (or "window") that one or more views are
  rendered to. Among other things, it has a height, width, background color, and
  a one or more `Views`.  (An orthoviewer, for example, would be 1 canvas with 3
  views, one for each axis.)
- **`core.View`**: A view is a 2D viewport onto a `Scene`, using a single
  `Camera` (see below).  A view also implements the CSS box model, with a width,
  height, padding, margin, border, etc...
- **`core.Scene`**: A scene is a collection/graph of `Nodes`, where nodes are
  the basic "world objects" in a scene.  The `Scene` class itself is just a
  regular `Node`, but given a special subclass name when used as the root node.

### `core.nodes`

All "world" objects are subclasses of `core.node.Node`.  This includes:

- **`core.nodes.Node`**: This base class implements the basic node
  functionality, including a `parent` and `children` property, and a `transform`
  property.  It has an `add()` method that should be used when adding children
  to a node. It also has general properties that all scene graph members share
  like `visible`, `opacity`, `name`, etc...

- **`core.nodes._data.DataNode`**:  A DataNode is a subclass of `Node` that
  implements the basic functionality for a node that has a `data` property (most
  Nodes will be DataNodes).  The main point of this base class is to:

  - implement the `data` property, which is an `EventedObjectProxy` that wraps
    the actual user provided data, and emits events when the data changes
    (allowing in-place modification of data, and still having the scene graph
    update)
  - Implements the logic for `DataField`s.  A `DataField` is a field on a
    `DataNode`, (much like a dataclass field or a pydantic field) that implies
    that the field requires access to the data.  For example, the `clim` field
    on Image can be either `AbsContrast` (which doesn't care about the data) or
    `PercentileContrast` (which is only meaningful with respect to the data).
    `DataFields` have an `apply` method that is called when the data changes,
    with the new data as the argument.  This allows the `DataField` to update
    itself based on the new data.

#### node types

Here is where most of the development needs to be done, (the 6-7 napari layer
types could be implemented as subclasses of `core.nodes.DataNode`).  Currently,
there is just one subclass for `Image` (which, probably along with points, will
be the most important node type to get right, and can serve as the primary
development target for a while).

- **`core.nodes.Image`**: A `DataNode` for displaying dense arrays as a 2D/3D
    image. Has a colormap, clim, gamma, and interpolation.
- ...

### `backend`

The backend module contains the code that implements the view.

The backend is currently implemented using [vispy](https://vispy.org/), but
[pygfx](https://pygfx.readthedocs.io/en/latest/) should also be implemented
as a way to ensure that we're not making any assumptions too specific to vispy.
(One can also imagine `pythreejs`, or other backends in the future).

The backend is responsible for:

- Rendering the scene graph to a canvas
- Handling the event loop

Most objects in the backend modules will be subclasses (or at least
implementations for) various Protocols defined in `core`.

For example, all `core.Node` objects require a backend object that
implements the `NodeBackend` protocol (with methods like `_viz_set_name`,
`_viz_add_node`, etc...).

### The `VisModel` pattern

You'll note that most of the `core` objects are subclasses of `VisModel`.

This is an important pattern (which should be critically re-evaluated often)
that mediates the relationship between the `core` and `backend` objects.  Let's
take a look at the `microvis.core.Canvas` class as an example.  It is defined
as:

```python
class Canvas(VisModel[CanvasBackend]):
  width: float = 500
  height: float = 500
  visible: bool = False
```

where `CanvasBackend` is a protocol defining the methods that a backend
must implement to be able to render a `Canvas`:

```python
from typing import Protocol

class CanvasBackend(Protocol):
    def _viz_set_width(self, arg: int) -> None: ...
    def _viz_set_height(self, arg: int) -> None: ...
    def _viz_set_visibile(self, arg: bool) -> None: ...
```

`VisModel` then, is a base class (it's a `Generic` parametrized by
a certain backend protocol) that:

1. Handles the fetching and creation of a backend adaptor object implementing
   the appropriate backend protocol (in the `backend_adaptor()` method).
1. makes sure that whenever any of the model attributes are changed, the
   corresponding backend setter method is called.

```python
canvas = Canvas()
canvas.width = 1000 # calls canvas._backend._viz_set_width(1000)
```

The logic for this is defined in `VisModel._on_any_event` ...
another method that should be critically re-evaluated often.

### `controller`

GUI elements that control the state of the model (e.g. sliders, buttons, etc...)
go here.  Note that currently, it is no more than a single simple function that
takes a model and returns a magicgui `Container`.

```python
def make_controller(model: EventedModel) -> Container:
  ...
```

It would be nice to try resist the urge to make this any more complex.  We will
certainly need ways to specify that certain model fields should or shouldn't be
included in the controller, and to perhaps composes layouts for combinations
of model objects, but I think we should try to keep it simple for now - and work
on improving magicgui rather than trying to make any elaborate solutions here.

## Usage

```python
from imageio.v3 import imread
from microvis.convenience import imshow

camera = imread("imageio:camera.png").copy()
canvas = imshow(camera)
```

:joy:

... where `imshow` is a convenience function that more or less does this:

```python
def imshow(image, **kwargs):
  canvas = Canvas()
  canvas.show()
  view = canvas.add_view()
  image = view.add_image(image, **kwargs)
return canvas
```

obviously, there's plenty of decisions to be made about the user-facing API,
including what the return objects should be, etc... So, for now, developers
should much about in the internals to get access to the core objects they need.
For example:

```python
view = canvas.views[0]
image = view.scene.children[0]

# and now you can programatically change the image attributes
# and the image should update:
image.cmap = 'hot'
image.clim = ...
```

> **Note** that there is not (yet) a "Viewer" like object here.  I think
> plenty of development can occur before deciding on what that should look
> like.  There may well be multiple convenience functions that construct
> different variants of a "Viewer" (e.g. `imshow` and `orthoshow`) ... or
> perhaps the convenience functions will take kwargs that help to configure
> the viewer.  Just not sure yet.  So, the emphasis is on building solid
> composable parts before deciding on exactly how they should be composed.
