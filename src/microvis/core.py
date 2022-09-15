from vispy import scene


def imshow(data, figsize=(800, 600), bgcolor="black"):
    # Prepare canvas
    canvas = scene.SceneCanvas(
        keys="interactive", size=figsize, show=True, bgcolor=bgcolor
    )
    # Prepare view
    view = canvas.central_widget.add_view()

    # Prepare image
    if data.ndim == 2:
        scene.visuals.Image(data, parent=view.scene)
        view.camera = scene.PanZoomCamera(aspect=1)
    else:
        scene.visuals.Volume(data, parent=view.scene)
        view.camera = scene.TurntableCamera(fov=0, azimuth=0, elevation=0)

    view.camera.set_range()
    canvas.show()
    return canvas
