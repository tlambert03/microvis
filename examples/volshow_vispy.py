import numpy as np
from magicgui import magicgui
from vispy import app, io, scene

# Read volume
vol1 = np.load(io.load_data_file("volume/stent.npz"))["arr_0"]
print(vol1)

# Prepare canvas
canvas = scene.SceneCanvas(keys="interactive", size=(800, 600), show=True)

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Create the volume visuals, only one is visible
volume1 = scene.visuals.Volume(vol1, parent=view.scene)

# Create three cameras (Fly, Turntable and Arcball)
fov = 60.0
cam = scene.cameras.ArcballCamera(parent=view.scene, fov=fov, name="Arcball")
view.camera = cam


@magicgui(fov={"widget_type": "FloatSlider", "max": 180}, auto_call=True)
def change_cam(fov: float = cam.fov):
    cam.fov = fov


if __name__ == "__main__":
    change_cam.show()
    app.run()
