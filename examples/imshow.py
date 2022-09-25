from imageio.v3 import imread

from microvis.convenience import imshow

camera = imread("imageio:camera.png").copy()

c = imshow(camera)
# temporary
v = c.views[0]
img = v.scene.children[0]
