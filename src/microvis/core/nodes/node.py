from __future__ import annotations

from abc import abstractmethod
from typing import ClassVar, Optional, Protocol, TypeVar

from .._base import Field, FrontEndFor, ModelBase, SupportsVisibility


class Transform(ModelBase):
    ...


NodeType = TypeVar("NodeType", bound="Node", contravariant=True)


# fmt: off
class NodeBackend(SupportsVisibility[NodeType], Protocol):
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
    def _viz_set_transform(self, arg: Transform | None) -> None: ...
    @abstractmethod
    def _viz_add_node(self, node: Node) -> None: ...
# fmt: on


NodeBackendType = TypeVar("NodeBackendType", bound="NodeBackend", covariant=True)


class Node(FrontEndFor[NodeBackendType]):
    """Base class for all nodes."""

    _BackendProtocol: ClassVar[type] = NodeBackend

    name: Optional[str] = Field(None, description="Name of the node.")
    parent: Optional[Node] = Field(
        None, description="Parent node. If None, this node is a root node."
    )
    children: list[Node] = Field(default_factory=list)  # immutable?
    visible: bool = Field(True, description="Whether this node is visible.")
    opacity: float = Field(1.0, description="Opacity of this node.", ge=0, le=1)
    order: int = Field(
        0,
        description="A value used to determine the order in which nodes are drawn. "
        "Greater values are drawn later. Children are always drawn after their parent",
    )
    interactive: bool = Field(
        False, description="Whether this node accepts mouse and touch events"
    )
    transform: Optional[Transform] = Field(
        None,
        description="Transform that maps the local coordinate frame to the coordinate "
        "frame of the parent.",
    )

    def __contains__(self, item: Node) -> bool:
        """Return True if this node is an ancestor of item."""
        return item in self.children

    def add(self, node: Node) -> None:
        """Add a child node."""
        self.children.append(node)
        if self.has_backend:
            self.backend_adaptor()._viz_add_node(node)
