from microvis.core.view import View, ViewBackend


def test_canvas(mock_backend: ViewBackend) -> None:
    view = View(position=(100, 120), size=(600, 650), background_color="red")
    assert view.size == (600.0, 650.0)
    assert view.background_color and view.background_color.as_named() == "red"

    # before show() is called, the backend should not be created
    assert not view.has_backend
    assert not mock_backend.method_calls  # type: ignore

    # once show() is called, the backend should be created and visible called
    view.show()

    # This is a bummer...
    # we'd *like* for `view.show()` to spin up a backend, and it will when vispy is
    # the chosen backend... but that's because of the logic in the vispy backend.
    # see FIXME note at ~L#30 in src/microvis/backend/vispy/_canvas.py
    assert not view.has_backend  # if this fails in the future, you win!

    assert view.backend_adaptor() is mock_backend
    mock_backend._viz_set_visible.assert_called_once_with(True)

    # canvas.width = 700
    # mock_backend._viz_set_width.assert_called_once_with(700)
    # canvas.height = 750
    # mock_backend._viz_set_height.assert_called_once_with(750)
    # canvas.size = (720, 770)
    # mock_backend._viz_set_width.assert_called_with(720)
    # mock_backend._viz_set_height.assert_called_with(770)
    # canvas.title = "MicroVis2"
    # mock_backend._viz_set_title.assert_called_once_with("MicroVis2")
    # canvas.background_color = "blue"
    # mock_backend._viz_set_background_color.assert_called_once_with(Color("blue"))

    # assert json.loads(canvas.json()) == {
    #     "width": 720.0,
    #     "height": 770.0,
    #     "background_color": "blue",
    #     "visible": True,
    #     "title": "MicroVis2",
    #     "views": [],
    # }

    # canvas.add_view()
    # assert canvas.json()  # smoke test to make sure we can still serialize everything.

    # canvas.render()
    # mock_backend._viz_render.assert_called_once()

    # canvas.hide()
    # mock_backend._viz_set_visible.assert_called_with(False)

    # canvas.close()
    # mock_backend._viz_close.assert_called_once()

    # # these should get passed to the backend object.
    # canvas._repr_mimebundle_(1, 2)
    # assert canvas.native._repr_mimebundle_.called_once_with(1, 2)
