import numpy as np
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QSlider, QVBoxLayout, QWidget
from skimage import data
from vispy import scene

# Prepare canvas
canvas = scene.SceneCanvas(keys="interactive", size=(800, 600), show=True)
view = canvas.central_widget.add_view(camera="panzoom")
view.camera.aspect = 1

cells = data.cells3d()[:, 0]
volume = scene.visuals.Volume(cells, parent=view.scene)
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
s2 = QSlider(Qt.Horizontal)
s3 = QSlider(Qt.Horizontal)


def update():
    if s1.sender() is s1:
        s2.setValue(max(s2.value(), s1.value() + 1))
    elif s1.sender() is s2:
        s1.setValue(min(s2.value() - 1, s1.value()))
    volume.clipping_planes = [
        [[0, 0, s1.value()], zhat],
        [[0, 0, s2.value()], -zhat],
    ]


s1.valueChanged.connect(update)
s2.valueChanged.connect(update)
s3.valueChanged.connect(update)
w.layout().addWidget(s1)
w.layout().addWidget(s2)
w.layout().addWidget(s3)
w.show()

if __name__ == "__main__":
    from vispy import app

    print(__doc__)
    app.run()
