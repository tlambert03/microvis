"""Basic playground of showing an image with vispy."""
import sys

import imageio.v3 as iio
from vispy import app, scene

# Create the image
img_data = iio.imread("imageio:astronaut.png")


canvas = scene.SceneCanvas(keys="interactive", size=(600, 600))
canvas.show()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()
# add image
image = scene.visuals.Image(img_data, parent=view.scene)

# Set 2D camera (the camera will scale to the contents in the scene)
view.camera = scene.PanZoomCamera(aspect=1)
# flip y-axis to have correct aligment
view.camera.flip = (0, 1, 0)
view.camera.set_range()
# view.camera.zoom(0.1, (250, 200))


if __name__ == "__main__" and sys.flags.interactive == 0:
    app.run()
