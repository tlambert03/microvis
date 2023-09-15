import sys

import imageio.v3 as iio
import pygfx as gfx
from qtpy.QtWidgets import QApplication
from wgpu.gui.auto import WgpuCanvas, run

app = QApplication([])

canvas = WgpuCanvas(size=(600, 600))
renderer = gfx.renderers.WgpuRenderer(canvas)
scene = gfx.Scene()

im = iio.imread("imageio:astronaut.png")

image = gfx.Image(
    gfx.Geometry(grid=gfx.Texture(im, dim=2)),
    gfx.ImageBasicMaterial(clim=(0, 255)),
)
scene.add(image)

camera = gfx.OrthographicCamera(512, 512)
camera.show_object(scene, view_dir=(0, 0, -1))
camera.local.scale_y = -1

controller = gfx.PanZoomController(camera)
controller.register_events(renderer)


def animate():
    renderer.render(scene, camera)
    canvas.request_draw()


if __name__ == "__main__" and sys.flags.interactive == 0:
    canvas.request_draw(animate)
    run()
