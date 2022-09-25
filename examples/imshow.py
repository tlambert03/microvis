from imageio.v3 import imread

from microvis.convenience import imshow

camera = imread("imageio:camera.png")

c = imshow(camera)
