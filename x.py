from skimage import data
from microvis import imshow

astro = data.astronaut()
v, img = imshow(astro, backend="vispy")
