from __future__ import annotations

from abc import abstractmethod
from typing import Any, Optional, Protocol, Sequence, TypeVar

from psygnal.containers import EventedList
from pydantic import validator

from ..._logs import logger
from .._base import Field, FrontEndFor, SupportsVisibility
from .._transform import Transform

NodeTypeCoV = TypeVar("NodeTypeCoV", bound="Node", covariant=True)
NodeType = TypeVar("NodeType", bound="Node")
NodeBackendTypeCoV = TypeVar("NodeBackendTypeCoV", bound="NodeBackend", covariant=True)


# fmt: off
class NodeBackend(SupportsVisibility[NodeTypeCoV], Protocol):
    """Backend interface for a Node."""

    @abstractmethod
    def _viz_set_name(self, arg: str) -> None: ...
    @abstractmethod
    def _viz_set_parent(self, arg: Node | None) -> None: ...
    @abstractmethod
    def _viz_set_children(self, arg: list[Node]) -> None: ...
    @abstractmethod
    def _viz_set_visible(self, arg: bool) -> None: ...
    @abstractmethod
    def _viz_set_opacity(self, arg: float) -> None: ...
    @abstractmethod
    def _viz_set_order(self, arg: int) -> None: ...
    @abstractmethod
    def _viz_set_interactive(self, arg: bool) -> None: ...
    @abstractmethod
    def _viz_set_transform(self, arg: Transform) -> None: ...
    @abstractmethod
    def _viz_add_node(self, node: Node) -> None: ...
# fmt: on


class NodeList(EventedList[NodeType]):
    _owner: Optional[Node] = None

    def _pre_insert(self, value: NodeType) -> NodeType:
        assert isinstance(value, Node), "Canvas views must be View objects"
        return super()._pre_insert(value)

    def _post_insert(self, new_item: NodeType) -> None:
        if self._owner is not None:
            self._owner.add(new_item)
        super()._post_insert(new_item)


class Node(FrontEndFor[NodeBackendTypeCoV]):
    """Base class for all nodes."""

    name: Optional[str] = Field(None, description="Name of the node.")
    parent: Optional[Node] = Field(
        None,
        description="Parent node. If None, this node is a root node.",
        exclude=True,  # prevents recursion in serialization.
        # TODO: maybe make children the derived field?
    )
    # make immutable?
    children: NodeList[Node] = Field(default_factory=NodeList, hide_control=True)
    visible: bool = Field(True, description="Whether this node is visible.")
    interactive: bool = Field(
        False, description="Whether this node accepts mouse and touch events"
    )
    opacity: float = Field(default=1.0, ge=0, le=1, description="Opacity of this node.")
    order: int = Field(
        0,
        ge=0,
        description="A value used to determine the order in which nodes are drawn. "
        "Greater values are drawn later. Children are always drawn after their parent",
        hide_control=True,
    )
    transform: Transform = Field(
        default_factory=Transform,
        description="Transform that maps the local coordinate frame to the coordinate "
        "frame of the parent.",
    )

    def __repr_args__(self) -> Sequence[tuple[str | None, Any]]:
        args = super().__repr_args__()
        # avoid recursion in repr
        return [a for a in args if a[0] != "parent"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.children._owner = self
        logger.debug(f"created {type(self)} node {id(self)}")

    def __contains__(self, item: Node) -> bool:
        """Return True if this node is an ancestor of item."""
        return item in self.children

    def add(self, node: Node) -> None:
        """Add a child node."""
        nd = f"{node.__class__.__name__} {id(node)}"
        slf = f"{self.__class__.__name__} {id(self)}"
        node.parent = self
        if node not in self.children:
            logger.debug(f"Adding node {nd} to {slf}")
            self.children.append(node)
            if self.has_backend:
                self.backend_adaptor()._viz_add_node(node)

    @classmethod
    def validate(cls, value: Any) -> Node:
        """Validate the node tree."""
        # don't validate existing Nodes ...
        # pydantic's `super().validate()` will result in the construction of a NEW
        # object, which is not what we want.
        return value if isinstance(value, cls) else super().validate(value)

    @validator("transform", pre=True)
    def _validate_transform(cls, v: Any) -> Any:
        return Transform() if v is None else v
