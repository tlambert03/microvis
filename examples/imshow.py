from imageio.v3 import imread

from microvis.controller import make_controller
from microvis.convenience import imshow

camera = imread("imageio:camera.png")
c = imshow(camera)
# temporary, just for convenience in testing
v = c.views[0]
img = v.scene.children[0]

# also optional... example for now
ctrl = make_controller(img)
ctrl.show()


if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication

    app = QApplication.instance()
    app.exec_()
