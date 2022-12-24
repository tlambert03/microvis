from imageio.v3 import imread
from qtpy.QtWidgets import QApplication

from microvis.controller import make_controller
from microvis.convenience import imshow
from microvis.core import Transform

app = QApplication.instance()
if not (had_app := bool(app)):  # had_app lets us only exec_ if we created the app
    app = QApplication([])

camera = imread("imageio:camera.png").copy()
c = imshow(camera, transform=Transform().scaled((0.5, 0.5)))
# temporary, just for convenience in testing
v = c.views[0]
img = v.scene.children[0]

# also optional... example for now
ctrl = make_controller(img)
ctrl.show()

had_app or app.exec_()
