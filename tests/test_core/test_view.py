import json

from microvis._types import Color
from microvis.core.nodes.camera import Camera
from microvis.core.nodes.scene import Scene
from microvis.core.view import View


def test_view(mock_backend) -> None:
    view = View(position=(100, 120), size=(600, 650), background_color="red")
    assert view.size == (600.0, 650.0)
    assert view.background_color and view.background_color.as_named() == "red"

    # before show() is called, the backend should not be created
    assert not view.has_adaptor
    assert not mock_backend

    # once show() is called, the backend should be created and visible called
    view.show()
    assert view.has_adaptor
    adaptor = view.backend_adaptor()
    assert view.visible
    adaptor._vis_set_camera.assert_called_once()
    adaptor._vis_set_scene.assert_called_once()

    new_cam = Camera()
    view.camera = new_cam
    adaptor._vis_set_camera.assert_called_with(new_cam)
    new_scene = Scene()
    view.scene = new_scene
    adaptor._vis_set_scene.assert_called_with(new_scene)
    view.size = (720, 770)
    adaptor._vis_set_size.assert_called_with((720, 770))
    view.background_color = "blue"
    adaptor._vis_set_background_color.assert_called_once_with(Color("blue"))
    view.border_width = 10
    adaptor._vis_set_border_width.assert_called_once_with(10)
    view.border_color = "green"
    adaptor._vis_set_border_color.assert_called_once_with(Color("green"))
    view.padding = 20
    adaptor._vis_set_padding.assert_called_once_with(20)
    view.margin = 30
    adaptor._vis_set_margin.assert_called_once_with(30)
    view.visible = False
    adaptor._vis_set_visible.assert_called_once_with(False)

    # Test serialization
    # If this becomes annoying to maintain (because of changing defaults, eg.)
    # it doesn't need to be so exhaustive.
    serdes: dict = json.loads(view.json())
    assert len(serdes.pop("children")) == 2
    assert serdes.pop("camera") == json.loads(new_cam.json())
    assert serdes.pop("scene") == json.loads(new_scene.json())
    assert serdes == {
        "name": None,
        "visible": False,
        "interactive": False,
        "opacity": 1.0,
        "order": 0,
        "transform": {
            "matrix": [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        },
        "position": [100.0, 120.0],
        "size": [720.0, 770.0],
        "background_color": "blue",
        "border_width": 10.0,
        "border_color": "green",
        "padding": 20,
        "margin": 30,
    }
