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

    assert not canvas.has_backend
    assert not view.has_backend
    assert not camera.has_backend

    # canvas.show()
    qtbot.addWidget(canvas.native_objects.native_objects)

    assert canvas.has_backend
    assert view.has_backend
    assert camera.has_backend
    assert image.has_backend

    canvas.dict()
    view.dict()


def test_serialization():
    c = Canvas()
    v = c.add_view()
    img = v.add_image(np.zeros((10, 10)))
    assert c.json()
    assert v.json()
    assert img.json()
