from typing import TYPE_CHECKING


from microvis import Canvas, View, Camera

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


def test_canvas(qtbot: "QtBot") -> None:
    canvas = Canvas()

    view = canvas.add_view()
    assert isinstance(view, View)
    assert view in canvas.views

    camera = view.camera
    assert isinstance(camera, Camera)

    assert not canvas.has_backend
    assert not view.has_backend
    assert not camera.has_backend

    # canvas.show()
    qtbot.addWidget(canvas.native.native)

    assert canvas.has_backend
    assert view.has_backend
    assert camera.has_backend

    canvas.dict()
    view.dict()
