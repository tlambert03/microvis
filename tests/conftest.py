from unittest.mock import patch
import pytest
import numpy as np

@pytest.fixture(autouse=True)
def _noshow():
    np.random.seed(10)

    with patch('microvis.core.Viewer.show', lambda self: None):
        yield
