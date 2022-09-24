from __future__ import annotations

import contextlib


def in_notebook() -> bool:
    """Determine if the user is executing in a Jupyter Notebook"""
    with contextlib.suppress(Exception):
        from IPython import get_ipython

        return get_ipython().__class__.__name__ == "ZMQInteractiveShell"
    return False


def in_ipython() -> bool:
    """Return true if we're running in an IPython interactive shell."""
    with contextlib.suppress(Exception):
        from IPython import get_ipython

        return get_ipython().__class__.__name__ == "TerminalInteractiveShell"
    return False
