from __future__ import annotations

import collections.abc
import re
from importlib import import_module
from typing import TYPE_CHECKING, Any, TypeVar, Union

from pydantic import BaseModel
from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.pages import Page

PYDANTIC_TABLE = re.compile(r"::: pydantic_table:([\w.]+)")


# HOOKS --- https://www.mkdocs.org/dev-guide/plugins/#events


def on_page_markdown(md: str, page: Page, config: MkDocsConfig, **_: Any) -> str:
    return PYDANTIC_TABLE.sub(lambda m: pydantic_table(m.group(1)), md)


# -----------------------------------

# Supporing functions


def _type_link(typ: Any) -> str:
    mod = f"{typ.__module__}." if typ.__module__ != "builtins" else ""
    if mod.startswith("microvis"):
        type_fullpath = f"{mod}{typ.__name__}"
        return f"[`{typ.__name__}`][{type_fullpath}]"
    return str(typ)


def _build_type_link(typ: Any) -> str:
    origin = getattr(typ, "__origin__", None)
    if origin is None:
        return _type_link(typ)

    args = getattr(typ, "__args__", ())
    if origin is collections.abc.Callable and any(
        isinstance(a, (TypeVar, ParamSpec)) for a in args
    ):
        return _type_link(origin)
    types = [_build_type_link(a) for a in args if a is not type(None)]
    if origin is Union:
        return " or ".join(types)
    type_ = ", ".join(types)
    return f"{_type_link(origin)}[{type_}]"


def pydantic_table(name: str, include_mkdocs_link: bool = True) -> str:
    """Build a markdown table from a pydantic model."""
    mod, attr = name.rsplit(".", 1)
    cls = getattr(import_module(mod), attr)
    if not issubclass(cls, BaseModel):
        raise ValueError(f"{name} is not a pydantic model")
    rows = ["| Field | Type | Description |", "| ----  | ---- | ----------- |"]
    for f in cls.__fields__.values():
        type_ = _build_type_link(f.outer_type_)
        row = f"| {f.name} | {type_} | {f.field_info.description} |"
        rows.append(row)
    output = "\n".join(rows) + "\n"
    if include_mkdocs_link:
        output += f"\n\n::: {name}\n\n"
    return output
