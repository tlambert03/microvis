# Contributing & Project Thoughts

Microvis is a pre-alpha experimental repo.  It is not published
on PyPI and is not yet intended for general use. But it would be
great to have eyes on it! And you're welcome to contribute.

What follows are some random thoughts on the organization, goals,
and philosophy of the project; and some pointers for getting
started and contributing.

## Motivation & Principles

"microvis" (a working name which will likely not stick), is a
data-visualization library.  It bears obvious similarities to
[napari](napari.org), and indeed, it is inspired by napari. It
can be thought of as a "reimagining" or a rewrite of napari with
a few considerations and principles in mind:

- **Emphasis on declarative models**

  It should be very clear from looking at the code what the
  attributes of a given object are, and there should be a single
  source of truth for those attributes.

- **The model should be very clearly separated from the view.**

  The model in microvis should be a pure data structure: easily
  **serializable** and deserializable, and easily attached/detached
  from a view.  (Difficulty with issues like
  [napari#3184](https://github.com/napari/napari/pull/3184) are
  a good example of the motivation for this principle.)

  - [ ] Tests for serializability/deserializability should be
        added from the beginning.  Interpolation between
        serialized states would also be nice to support from
        the beginning (as in napari-animation)

  - [ ] Every object that connects to the events of another
        object should have a clear `disconnect` method.

  - [ ] Instantiating and interacting with a model should not
        require a view.  The backend should not be invoked or
        even imported until the model is attached to a view,
        (via a `show()` method or similar).

  - [ ] There should be nothing wrong with connecting the same
        model instance to multiple views, or even multiple
        backends... and it should be possible to destroy a view
        without destroying the model.

- **Clear backend abstraction**

  There should be no assumptions about the GUI framework or
  visualization backend in the model or view code. Any
  interaction with backends like vispy should be done via
  a clearly defined interface (such that any other backend
  could be substituted in in the future).  As an initial
  example, microvis should work with both vispy and pygfx.
  (There is a branch with pygfx working... but vispy has
  been the reference backend so far.)

- **GUI should be minimal and contstructed from the models**

  At first at least, custom GUI elements should be avoided.
  The GUI should be preferably be constructed from the
  models themselves (support for [dataclasses in
  `magicgui`](https://github.com/pyapp-kit/magicgui/pull/498)
  was largely inspired by the desire to do this.)

- **The app *should* work in the browser**

  An early decision in napari was to focus on the desktop
  application, and browser support was an explicit non-goal.
  However, lack of browser support made remote usage (e.g.
  via jupyter notebooks running on a remote server) difficult.
  The inability to embed directly in a juptyer notebook is a
  limitation that prevents napari from being "easily" used
  in a lot of contexts (both in the classroom and in exploratory
  data analysis).  microvis should go anywhere.

  - [jupyter-rfb](https://jupyter-rfb.readthedocs.io/en/latest/)
    is a great example of a library that makes it easy to
    embed a vispy canvas in a jupyter notebook, and the vispy
    backend here already supports it.
  - [pygfx](https://github.com/pygfx/pygfx) can also run in the
    browser, and is based on [WGPU](https://github.com/pygfx/wgpu-py)
    instead of OpenGl. Maintaining tests for both backends will
    be a good way to ensure that the model is backend agnostic.

- **GUI controllers should *also* work in the browser**

  magicgui's support for ipywidgets means that, in theory, as
  long as we stick to autogenerating GUIs from the models (and
  limit the use of custom widgets), both the view and the control
  elements should be able to run in the browser.

- **The core should be lightweight**

  The code should import and the the view should spin up as fast
  as possible.  This means that microvis code itself should be
  very fast to import, and heavier backend dependencies should
  be lazy-loaded when a view is required.

  If any larger application-like functionality is needed, it
  should ideally be provided by a separate package.

- **The underlying scene-graph should not be compromised**

  Vispy and pygfx both have very powerful scene-graphs, and
  this library should not compromise that power. In napari,
  the original design was a flat list of layers: *napari*
  used the scene graph, but did not expose it to the user.
  The effort to add layer groups to napari (in essence
  "recovering" and exposing the scene graph) was a lot of
  work, and is still not complete.

  Unless we *explicitly* decide that the underlying scene-graph
  is not important to expose, it should be exposed.

- **Multiple canvas & multi-view support**

  Multi-canvas and ortho-view support in napari is one of the
  earliest and most requested features, but still remains
  challenging without somewhat "abusing" the API (e.g. by
  creating an
  [independent, synchronized model](https://github.com/napari/napari/blob/main/examples/multiple_viewer_widget.py)
  for each view, rather than just adding a new view onto the
  same model with a different camera.

  Microvis should support multiple views and multiple canvases
  from the beginning (with orthoviews being just one example).

- **In place data mutation should be reflected in the view**

  In napari, it often surprises people that in-place mutations
  to `layer.data` don't update the view, like all the other
  attributes.  The philosophy was that the `data` objects should
  be as raw as possible (essentially untouched by napari), but
  this had some unfortunate consequences.  microvis should not
  be opposed to wrapping data objects in a way that allows for
  in-place mutation to trigger updates (but from the user's perspective,
  the API of the wrapped object should not be changed).

- **well defined data interfaces**

  It should be clearer from the beginning what data types
  are supported, using Protocols to define *every* method or
  attribute that is required to be present on a data object.

- **Typing and testing**

  Even if it adds a degree of complexity for new contributors,
  microvis should be fully typed, and should have an excellent
  test suite. Slow development of stable, well-tested code is
  better than fast development of untested code.

- **User extendability**

  Extending the builtin layer models of napari has proven a bit difficult due to
  a lot of internal interdependencies.  As an example, the awesome particle
  layer in <https://github.com/napari-storm/napari-storm> was very challenging
  to implement as a plugin, and remains difficult to add to napari core.
  microvis should make it easy to extend the builtin nodes and models, *and*
  clear how to extend one or more backends to support their new object. For GUI
  controls here, if we stick to magicgui for dynamically creating the GUI from
  the models, extensions will get GUI controls for free. (See
  `examples/custom_node.py` for an example of how this could work.)

- **Non-goals**

  Until the above goals are met, microvis should not focus on

  - preferences and persistent settings
  - plugins

## Dependencies

- [psygnal](https://github.com/pyapp-kit/psygnal), implements
  the [observer pattern](https://en.wikipedia.org/wiki/Observer_pattern).
  Most of the models here are evented models, as in napari, but
  backed by psygnal instead of napari's events. (Currently, they
  are pydantic models, but it would be nice to try to make them
  plain dataclasses and see how that feels).  Models emit events
  when their attributes change, and the view listens to those.

- [magicgui](https://github.com/pyapp-kit/magicgui).  Unless it becomes
  super annoying, it would be best to stick to magicgui for all GUI
  elements, since it can be used in the browser as well as desktop.
  This will come at the expense of customizability, but it's a
  tradeoff that I think is worth it at this point.  Magicgui acts
  as a controller for the models.

## Contributing

### Setting up local development

```bash
git clone https://github.com/tlambert03/microvis.git
cd microvis
pip install -e .[dev]
```

### Building the docs

(not that there's much to build, but still)

```bash
mkdocs serve
```

### Running tests

Tests are still very sparse, since the API and core is still
very much in flux. But you can run them with:

```bash
pip install -e .[test]
pytest
```

## Examples

see the `examples` folder... They're crap at the moment, but
should be developed.
