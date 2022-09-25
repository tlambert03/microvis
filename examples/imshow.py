from skimage import data

from microvis.convenience import imshow

c = imshow(data.camera())
v = c.views[0]
