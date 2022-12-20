try:
    import pytestqt  # noqa: F401
except Exception:
    import pytest

    pytest.skip("qtpy not installed", allow_module_level=True)
