from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

from microvis.core._vis_model import VisModel

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def mock_backend(monkeypatch: MonkeyPatch) -> None:
    # the subclass is needed to prevent args from being passed to the MagicMock.__init__
    class AdaptorMock(MagicMock):
        def __init__(self, *_: Any, **__: Any) -> None:
            super().__init__()

    # In reality VisModel._get_adaptor_class would return a class, and the
    # init of that class accepts one argument, the VisModel instance.
    # Here we just return a MagicMock, and avoid engaging any backends
    def _get_adaptor_class(*_: Any, **__: Any) -> type[MagicMock]:
        return AdaptorMock

    monkeypatch.setattr(VisModel, "_get_adaptor_class", _get_adaptor_class)
