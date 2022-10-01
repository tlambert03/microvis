from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from typing import Iterable, Protocol

    class _SupportsChildren(Protocol):
        children: Iterable[_SupportsChildren]


def in_notebook() -> bool:
    """Determine if the user is executing in a Jupyter Notebook."""
    with contextlib.suppress(Exception):
        from IPython import get_ipython

        # sourcery skip: remove-unnecessary-cast
        return bool(get_ipython().__class__.__name__ == "ZMQInteractiveShell")
    return False


def in_ipython() -> bool:
    """Return true if we're running in an IPython interactive shell."""
    with contextlib.suppress(Exception):
        from IPython import get_ipython

        # sourcery skip: remove-unnecessary-cast
        return bool(get_ipython().__class__.__name__ == "TerminalInteractiveShell")
    return False


def _simple_repr(obj: object) -> str:
    return f"{obj.__class__.__name__} {hex(id(obj))}"


def strf_tree(
    obj: _SupportsChildren,
    level: int = 0,
    represent: Callable[[object], str] | None = _simple_repr,
) -> str:
    """Format a tree of objects as a string."""
    indent = "  "
    represent = represent or repr
    ret = indent * level + represent(obj) + "\n"
    for child in obj.children:
        ret += strf_tree(child, level + 1)
    return ret


def print_tree(
    obj: _SupportsChildren, represent: Callable[[object], str] | None = _simple_repr
) -> None:
    """Pretty print a tree of objects."""
    print(strf_tree(obj, represent=represent))
