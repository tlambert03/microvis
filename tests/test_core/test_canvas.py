import json

from microvis._types import Color
from microvis.core.canvas import Canvas


def test_canvas(mock_backend) -> None:
    canvas = Canvas(width=600, height=650, title="MicroVis", background_color="red")
    # assert canvas.size == (600.0, 650.0)
    assert canvas.width == 600.0
    assert canvas.height == 650.0
    assert canvas.title == "MicroVis"
    assert canvas.background_color and canvas.background_color.as_named() == "red"

    # before show() is called, the backend should not be created
    assert not canvas.has_adaptor

    # once show() is called, the backend should be created and visible called
    canvas.show()
    assert canvas.has_adaptor
    adaptor = canvas.backend_adaptor()
    adaptor._vis_set_visible.assert_called_once_with(True)

    canvas.width = 700
    adaptor._vis_set_width.assert_called_once_with(700)
    canvas.height = 750
    adaptor._vis_set_height.assert_called_once_with(750)
    canvas.size = (720, 770)
    adaptor._vis_set_width.assert_called_with(720)
    adaptor._vis_set_height.assert_called_with(770)
    canvas.title = "MicroVis2"
    adaptor._vis_set_title.assert_called_once_with("MicroVis2")
    canvas.background_color = "blue"
    adaptor._vis_set_background_color.assert_called_once_with(Color("blue"))

    assert json.loads(canvas.json()) == {
        "width": 720.0,
        "height": 770.0,
        "background_color": "blue",
        "visible": True,
        "title": "MicroVis2",
        "views": [],
    }

    canvas.add_view()
    assert canvas.json()  # smoke test to make sure we can still serialize everything.

    canvas.render()
    adaptor._vis_render.assert_called_once()

    canvas.hide()
    adaptor._vis_set_visible.assert_called_with(False)

    canvas.close()
    adaptor._vis_close.assert_called_once()

    # these should get passed to the backend object.
    canvas._repr_mimebundle_(1, 2, x=1)  # random args, kwargs
    assert mock_backend._viz_get_ipython_mimebundle.called_once_with(1, 2, x=1)
