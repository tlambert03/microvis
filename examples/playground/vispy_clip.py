import numpy as np
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QSlider, QVBoxLayout, QWidget
from skimage import data
from vispy import scene

# Prepare canvas
canvas = scene.SceneCanvas(keys="interactive", size=(800, 600), show=True)
grid = canvas.central_widget.add_grid()
view = grid.add_view(row=0, col=0, camera="panzoom")
view.camera.aspect = 1
view2 = grid.add_view(row=0, col=1, camera="panzoom")
view2.camera.aspect = 1
view2.camera = view.camera

cells = data.cells3d()[:, 0]
volume = scene.visuals.Volume(
    cells, parent=view.scene, interpolation="nearest", clim=[0, 25000]
)
view.camera.set_range()


# since volume data is in 'zyx' coordinates, we have to reverse the coordinates
# we use as a center
volume_center = (np.array(cells.shape) / 2)[::-1]

xhat = np.array([1, 0, 0])
yhat = np.array([0, 1, 0])
zhat = np.array([0, 0, 1])

print(volume_center)
volume.clipping_planes = [[[0, 0, 30], zhat]]


w = QWidget()
w.setLayout(QVBoxLayout())

s1 = QSlider(Qt.Horizontal)
s1.setRange(0, len(cells) - 1)
# s2 = QSlider(Qt.Horizontal)
# s2.setRange(0, len(cells) - 1)


@s1.valueChanged.connect
def update():
    zhat = np.array([0, 0, 1])
    volume.clipping_planes = [
        [[0, 0, s1.value()], zhat],
        [[0, 0, s1.value() + 1], -zhat],
    ]


# s2.valueChanged.connect(update)
# s3.valueChanged.connect(update)
# w.layout().addWidget(s3)
w.layout().addWidget(s1)
# w.layout().addWidget(s2)
w.show()

if __name__ == "__main__":
    from vispy import app

    print(__doc__)
    app.run()
