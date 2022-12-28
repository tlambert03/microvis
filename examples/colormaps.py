from imageio.v3 import imread
from palettable.colorbrewer.sequential import Blues_8

import cmap

my_cmap = cmap.Colormap("my_cmap")
img_data = imread("imageio:camera.png")

viewer = "matplotlib"

if viewer == "matplotlib":
    import matplotlib.pyplot as plt

    # cmap.register_cmaps_with_matplotlib()

    plt.imshow(img_data, cmap=Blues_8.mpl_colormap)
    plt.show()
elif viewer == "napari":
    import napari

    cmap.register_cmaps_with_napari()

    v = napari.Viewer()
    v.add_image(img_data, colormap=my_cmap)
    napari.run()
elif viewer == "vispy":
    from vispy import app, scene

    cmap.register_cmaps_with_vispy()

    canvas = scene.SceneCanvas(keys="interactive")
    canvas.size = 800, 600
    canvas.show()
    view = canvas.central_widget.add_view()
    view.camera = scene.PanZoomCamera(aspect=1)
    image = scene.visuals.Image(img_data, cmap=my_cmap, parent=view.scene)
    # flip y-axis to have correct aligment
    view.camera.flip = (0, 1, 0)
    view.camera.set_range()
    app.run()
elif viewer == "microvis":

    from microvis import _util, imshow

    cmap.register_cmaps_with_vispy()
    with _util.exec_if_new_qt_app():
        imshow(img_data, cmap=my_cmap)
