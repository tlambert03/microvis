from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from microvis.core._base import FrontEndFor

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def mock_backend(monkeypatch: MonkeyPatch) -> None:
    mock = MagicMock()

    def _get_mock_backend_obj(
        self: FrontEndFor,
        backend_kwargs: dict | None = None,
        backend: str = "",
        class_name: str = "",
    ) -> object:
        return mock

    monkeypatch.setattr(FrontEndFor, "_get_backend_obj", _get_mock_backend_obj)
    yield mock
