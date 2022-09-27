from imageio.v3 import imread

from microvis.convenience import imshow
from microvis.controller import make_controller

camera = imread("imageio:camera.png").copy()
c = imshow(camera)
# temporary, just for convenience in testing
v = c.views[0]
img = v.scene.children[0]

# also optional... example for now
ctrl = make_controller(img)
ctrl.show()
