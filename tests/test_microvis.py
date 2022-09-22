import os

import numpy as np
import pytest

from microvis import imshow

BACKENDS = ["vispy"]
if os.getenv("CI") is not None:
    BACKENDS += ["pygfx"]


@pytest.mark.parametrize("backend", BACKENDS)
def test_something(qtbot, backend):
    data = np.random.randint(0, 255, (64, 64), dtype=np.uint8)
    viewer, img = imshow(data, size=data.shape, clim=(0, 255), backend=backend)
    rendered = viewer.canvas.render()
    assert rendered.shape == data.shape + (4,)
    # np.testing.assert_array_equal(rendered[:, :, 1], data)
