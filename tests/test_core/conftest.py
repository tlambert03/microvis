from __future__ import annotations

from typing import TYPE_CHECKING, Callable
from unittest.mock import MagicMock

import pytest

from microvis.core._vis_model import VisModel

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def mock_backend(monkeypatch: MonkeyPatch) -> None:
    mock = MagicMock()

    def _get_adaptor_type(
        self: VisModel, backend: str = "", class_name: str = ""
    ) -> Callable:
        # In reality VisModel._get_adaptor_type would return a class, and the
        # init of that class accepts one argument, the VisModel instance.
        # Here we mock that class with a callable that returns a mock
        # instance.  We do it so that we can yield the mock instance easily
        # in the test.
        return lambda self: mock

    monkeypatch.setattr(VisModel, "_get_adaptor_type", _get_adaptor_type)
    yield mock
