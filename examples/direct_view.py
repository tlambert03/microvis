"""Skip canvas creation"""
from imageio.v3 import imread

from microvis import View

view = View()
view.add_image(imread("imageio:camera.png"))

view.show()
