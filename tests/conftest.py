from unittest.mock import patch

import numpy as np
import pytest


@pytest.fixture(autouse=True)
def _noshow():
    np.random.seed(10)

    with patch("microvis.core.Viewer.show", lambda self: None):
        yield
