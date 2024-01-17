from imageio.v3 import imread

from microvis._util import exec_if_new_qt_app
from microvis.controller import make_controller
from microvis.convenience import imshow

camera = imread("imageio:camera.png").copy()

with exec_if_new_qt_app():
    c = imshow(camera)
    # temporary, just for convenience in testing
    v = c.views[0]
    img = v.scene.children[0]

    # also optional... example for now
    ctrl = make_controller(img)
    ctrl.show()
