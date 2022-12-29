"""Example using our cmap object with various image viewing libraries."""
import sys

import numpy as np
from imageio.v3 import imread

import cmap


def mpl_imshow(img_data: np.ndarray, cmap: cmap.LinearColormap) -> None:
    import matplotlib.pyplot as plt

    plt.imshow(img_data, cmap=cmap.to_mpl())
    plt.show()


def napari_imshow(img_data: np.ndarray, cmap: cmap.LinearColormap) -> None:
    import napari

    napari.view_image(img_data, colormap=cmap.to_napari())
    napari.run()


def microvis_imshow(img_data: np.ndarray, cmap: cmap.LinearColormap) -> None:
    from microvis import _util, imshow

    with _util.exec_if_new_qt_app():
        imshow(img_data, cmap=cmap)


def vispy_imshow(img_data: np.ndarray, cmap: cmap.LinearColormap) -> None:
    from vispy import app, scene

    canvas = scene.SceneCanvas(keys="interactive")
    canvas.size = 800, 600
    canvas.show()
    view = canvas.central_widget.add_view()
    view.camera = scene.PanZoomCamera(aspect=1)
    scene.visuals.Image(img_data, cmap=cmap.to_vispy(), parent=view.scene)
    view.camera.flip = (0, 1, 0)
    view.camera.set_range()
    app.run()


def pygfx_imshow(img_data: np.ndarray, cmap: cmap.LinearColormap) -> None:
    import pygfx as gfx
    from qtpy.QtWidgets import QApplication
    from wgpu.gui.auto import WgpuCanvas, run

    _ = QApplication.instance() or QApplication(sys.argv)
    canvas = WgpuCanvas(size=img_data.shape)
    renderer = gfx.renderers.WgpuRenderer(canvas)
    camera = gfx.OrthographicCamera(*img_data.shape)
    camera.position.y = img_data.shape[0] / 2
    camera.position.x = img_data.shape[1] / 2
    camera.scale.y = -1

    scene = gfx.Scene()
    scene.add(
        gfx.Image(
            gfx.Geometry(grid=gfx.Texture(img_data, dim=2)),
            gfx.ImageBasicMaterial(clim=(0, img_data.max()), map=cmap.to_pygfx()),
        )
    )

    def animate() -> None:
        renderer.render(scene, camera)
        canvas.request_draw()

    canvas.request_draw(animate)
    run()


def bokeh_imshow(img_data: np.ndarray, cmap: cmap.LinearColormap) -> None:
    from bokeh.plotting import figure, show

    p = figure()
    p.image(
        image=[np.flipud(img_data)],
        x=0,
        y=0,
        dw=img_data.shape[1],
        dh=img_data.shape[0],
        color_mapper=cmap.to_bokeh(),
    )
    show(p)


def altair_chart(cmap: cmap.LinearColormap) -> None:
    # altair doesn't do images well... using random data
    import altair as alt
    import pandas as pd

    alt.renderers.enable("altair_viewer")

    values = np.random.randn(100).cumsum()
    data = pd.DataFrame(
        {"value": values},
        index=pd.date_range("2018", freq="D", periods=100),
    )
    chart = (
        alt.Chart(data.reset_index())
        .mark_circle()
        .encode(
            x="index:T",
            y="value:Q",
            color=alt.Color(
                "value",
                scale=alt.Scale(
                    domain=(values.min(), values.max()),
                    # this is the important part
                    range=[c.hex for c in cmap.iter_colors()],
                ),
            ),
        )
    )
    chart.show()


def skimage_imshow(img_data: np.ndarray, cmap: cmap.LinearColormap) -> None:
    from skimage import io

    # skimage.imshow is just matplotlib
    io.imshow(img_data, cmap=cmap.to_mpl())
    io.show()


my_cmap = cmap.LinearColormap(["blue", (0.001, "black"), (0.999, "white"), "red"])
img_data = imread("imageio:camera.png")

viewer = sys.argv[1] if len(sys.argv) > 1 else "matplotlib"

if viewer == "matplotlib":
    mpl_imshow(img_data, my_cmap)
elif viewer == "microvis":
    microvis_imshow(img_data, my_cmap)
elif viewer == "napari":
    napari_imshow(img_data, my_cmap)
elif viewer == "vispy":
    vispy_imshow(img_data, my_cmap)
elif viewer == "pygfx":
    pygfx_imshow(img_data, my_cmap)
elif viewer == "bokeh":
    bokeh_imshow(img_data, my_cmap)
elif viewer == "altair":
    altair_chart(my_cmap)
elif viewer == "skimage":
    skimage_imshow(img_data, my_cmap)
elif viewer == "all":
    mpl_imshow(img_data, my_cmap)
    microvis_imshow(img_data, my_cmap)
    napari_imshow(img_data, my_cmap)
    vispy_imshow(img_data, my_cmap)
    pygfx_imshow(img_data, my_cmap)
    bokeh_imshow(img_data, my_cmap)
    altair_chart(my_cmap)
    skimage_imshow(img_data, my_cmap)
