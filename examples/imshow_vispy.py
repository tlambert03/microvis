"""Basic playground of showing an image with vispy."""
import sys

from vispy import app, scene
from vispy.io import load_data_file, read_png

# Create the image
img_data = read_png(load_data_file("mona_lisa/mona_lisa_sm.png"))


canvas = scene.SceneCanvas(keys="interactive", size=(800, 600))
canvas.show()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()
# add image
image = scene.visuals.Image(img_data, parent=view.scene)

# Set 2D camera (the camera will scale to the contents in the scene)
view.camera = scene.PanZoomCamera()
# flip y-axis to have correct aligment
view.camera.flip = (0, 1, 0)
view.camera.set_range()
# view.camera.zoom(0.1, (250, 200))


if __name__ == "__main__" and sys.flags.interactive == 0:
    app.run()
