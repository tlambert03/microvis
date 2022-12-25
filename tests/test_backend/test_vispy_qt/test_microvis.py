from typing import TYPE_CHECKING

import numpy as np

from microvis import Camera, Canvas, Image, View

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot

np.random.seed(10)


def test_canvas(qtbot: "QtBot") -> None:
    canvas = Canvas()

    view = canvas.add_view()
    assert isinstance(view, View)
    assert view in canvas.views

    camera = view.camera
    assert isinstance(camera, Camera)

    data = np.random.random((10, 10)).astype(np.float32)
    image = view.add_image(data)
    assert image in view.scene
    assert isinstance(image, Image)
    np.testing.assert_array_equal(image.data, data)

    assert not canvas.has_adaptor
    assert not view.has_adaptor
    assert not camera.has_adaptor

    canvas.show(backend="vispy")
    vispy_canvas = canvas.backend_adaptor("vispy")._vis_get_native()
    qtbot.addWidget(vispy_canvas.native)

    assert canvas.has_adaptor
    assert view.has_adaptor
    assert camera.has_adaptor
    assert image.has_adaptor

    canvas.dict()
    view.dict()


def test_serialization():
    c = Canvas()
    v = c.add_view()
    img = v.add_image(np.zeros((10, 10)))
    assert c.json()
    assert v.json()
    assert img.json()
