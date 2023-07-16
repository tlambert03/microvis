from typing import Any, ClassVar
from unittest.mock import Mock, patch

import numpy as np
import pytest

from microvis.backend import vispy
from microvis.core import _vis_model
from microvis.core.nodes._data import DataNode


def test_custom_node(qapp) -> None:
    """Test the BACKEND_ADAPTORS class attribute API for DataNode."""
    mock = Mock()

    class CustomVispyAdaptor(vispy.Node):
        def __init__(self, obj: "CustomNode", **backend_kwargs: Any) -> None:
            mock(obj, **backend_kwargs)

        def _vis_set_size(self, size: int) -> None:
            mock(size=size)

    class CustomNode(DataNode):
        BACKEND_ADAPTORS: ClassVar[dict] = {"vispy": CustomVispyAdaptor}
        size: int = 10

    custom_node = CustomNode(np.random.rand(20, 2))

    # test that the backend adaptor is created correctly
    assert mock.call_count == 0
    backend = custom_node.backend_adaptor()
    mock.assert_called_once_with(custom_node)
    assert isinstance(backend, CustomVispyAdaptor)

    # test that the backend adaptor is called correctly
    custom_node.size = 20
    mock.assert_called_with(size=20)


def test_custom_node_bad_backend() -> None:
    class DumbBackend:
        """Doesn't implement the necessary methods for a backend adaptor."""

    class CustomNode(DataNode):
        BACKEND_ADAPTORS: ClassVar[dict] = {"__TEST__": DumbBackend}  # type: ignore
        size: int = 10

    custom_node = CustomNode(np.random.rand(20, 2))
    with patch.object(_vis_model, "_get_default_backend", return_value="__TEST__"):
        with pytest.raises(ValueError, match="cannot be used as a backend object"):
            custom_node.backend_adaptor()
