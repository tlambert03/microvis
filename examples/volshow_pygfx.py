import sys

import imageio.v3 as iio
import pygfx as gfx
from qtpy.QtWidgets import QApplication
from wgpu.gui.auto import WgpuCanvas, run

app = QApplication([])

canvas = WgpuCanvas()
renderer = gfx.renderers.WgpuRenderer(canvas)
scene = gfx.Scene()

voldata = iio.imread("imageio:stent.npz").astype("float32")

geometry = gfx.Geometry(grid=voldata)
material = gfx.VolumeRayMaterial(clim=(0, 2000))

vol1 = gfx.Volume(geometry, material)
scene.add(vol1)


camera = gfx.PerspectiveCamera(fov=50, aspect=16 / 9)
camera.show_object(scene, view_dir=(-1, -1, -1), up=(0, 0, 1))
controller = gfx.OrbitController(camera, register_events=renderer)


def animate():
    renderer.render(scene, camera)
    canvas.request_draw()


if __name__ == "__main__" and sys.flags.interactive == 0:
    canvas.request_draw(animate)
    run()
