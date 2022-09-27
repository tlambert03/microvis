"""Skip canvas creation"""
from microvis import View
from imageio.v3 import imread

view = View()
view.add_image(imread("imageio:camera.png"))

view.show()
