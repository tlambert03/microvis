from imageio.v3 import imread

from microvis.controller import make_controller
from microvis.convenience import imshow
from microvis.core import Transform

camera = imread("imageio:camera.png").copy()
c = imshow(camera, transform=Transform().scaled((0.5, 0.5)))
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
