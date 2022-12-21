from __future__ import annotations

import importlib.util
import platform
import sys
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from sys import _version_info
    from typing import Iterable, Protocol

    class _SupportsChildren(Protocol):
        children: Iterable[_SupportsChildren]


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
    print(strf_tree(obj, represent=represent))  # noqa: T201


class Shell(str, Enum):
    IPYTHON = "ipython"
    JUPYTER = "jupyter"
    PYTHON = "python"

    def __str__(self) -> str:
        return self.value


@dataclass
class Context:
    shell: Shell
    sys_version: _version_info
    platform_system: str
    vispy_available: bool
    pygfx_available: bool
    qt_available: bool


_CONTEXT: Context | None = None


def get_context() -> Context:
    """Get the context in which the application is running.

    Returns
    -------
    Context
        A dataclass containing information about the context.  Includes attributes:
        shell, sys_version, platform_system, vispy_available, pygfx_available,
        qt_available.
    """
    global _CONTEXT
    if _CONTEXT is None:
        IPython = sys.modules.get("IPython")
        if IPython is not None:
            _shell = type(IPython.get_ipython()).__name__
            shell: Shell
            if _shell == "TerminalInteractiveShell":
                shell = Shell.IPYTHON
            elif _shell == "ZMQInteractiveShell":
                shell = Shell.JUPYTER
            else:
                shell = Shell.PYTHON

        qt_available = importlib.util.find_spec("qtpy") and any(
            importlib.util.find_spec(name)
            for name in ("PyQt5", "PySide2", "PyQt6", "PySide6")
        )

        _CONTEXT = Context(
            shell=shell,
            sys_version=sys.version_info,
            platform_system=platform.system(),
            vispy_available=bool(importlib.util.find_spec("vispy")),
            pygfx_available=bool(importlib.util.find_spec("pygfx")),
            qt_available=bool(qt_available),
        )
    return _CONTEXT  # noqa: RET504
