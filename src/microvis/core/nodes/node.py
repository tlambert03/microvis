from __future__ import annotations

from abc import abstractmethod
from typing import Any, Iterator, Optional, Protocol, Sequence, TypeVar

from psygnal.containers import EventedList
from pydantic import validator

from microvis._logger import logger
from microvis.core._base import Field, FrontEndFor, SupportsVisibility
from microvis.core._transform import Transform

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
        if not isinstance(value, Node):
            raise TypeError("Canvas views must be View objects")
        return super()._pre_insert(value)

    def _post_insert(self, new_item: NodeType) -> None:
        if self._owner is not None:
            self._owner.add(new_item)
        super()._post_insert(new_item)


class Node(FrontEndFor[NodeBackendTypeCoV]):  # type: ignore  # FIXME
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

    # FIXME: the presence of this `__init__` method breaks the very nice static
    # hints provided in VScode. but currently need it in order to add _owner to
    # children.  maybe there's a better way?
    # One possibility is to make _children a private (immutable) property that
    # can only be modified using `add()` method, then modify it as needed only on
    # first access.
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

    # below borrowed from vispy.scene.Node

    def transform_to_node(self, other: Node) -> Transform:
        """Return Transform that maps from coordinate frame of `self` to `other`.

        Note that there must be a _single_ path in the scenegraph that connects
        the two entities; otherwise an exception will be raised.

        Parameters
        ----------
        other : instance of Node
            The other node.

        Returns
        -------
        transform : instance of ChainTransform
            The transform.
        """
        a, b = self.path_to_node(other)
        tforms = [n.transform for n in a[:-1]] + [n.transform.inv() for n in b]
        return Transform.chain(*tforms[::-1])

    def path_to_node(self, other: Node) -> tuple[list[Node], list[Node]]:
        """Return two lists describing the path from this node to another.

        Parameters
        ----------
        other : instance of Node
            The other node.

        Returns
        -------
        p1 : list
            First path (see below).
        p2 : list
            Second path (see below).

        Notes
        -----
        The first list starts with this node and ends with the common parent
        between the endpoint nodes. The second list contains the remainder of
        the path from the common parent to the specified ending node.

        For example, consider the following scenegraph::

            A --- B --- C --- D
                   \
                    --- E --- F

        Calling `D.node_path(F)` will return::

            ([D, C, B], [E, F])

        """
        my_parents = list(self.iter_parents())
        their_parents = list(other.iter_parents())
        common_parent = next((p for p in my_parents if p in their_parents), None)
        if common_parent is None:
            slf = f"{self.__class__.__name__} {id(self)}"
            nd = f"{other.__class__.__name__} {id(other)}"
            raise RuntimeError(f"No common parent between nodes {slf} and {nd}.")

        up = my_parents[: my_parents.index(common_parent) + 1]
        down = their_parents[: their_parents.index(common_parent)][::-1]
        return (up, down)

    def iter_parents(self) -> Iterator[Node]:
        """Return list of parents starting from this node.

        The chain ends at the first node with no parents.
        """
        yield self

        x = self
        while True:
            try:
                parent = x.parent
            except Exception:
                break
            if parent is None:
                break
            yield parent
            x = parent
