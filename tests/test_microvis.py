from microvis import imshow
import numpy as np


def test_something():
    data = np.random.randint(0, 255, (64, 64), dtype=np.uint8)
    viewer = imshow(data, size=data.shape, clim=(0, 255))
    rendered = viewer.canvas.render()
    assert rendered.shape == data.shape + (4,)
    np.testing.assert_array_equal(rendered[:, :, 1], data)
