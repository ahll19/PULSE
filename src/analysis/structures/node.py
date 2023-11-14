from __future__ import annotations
from typing import List

from anytree import Node as RenderTreeNode


class Node(RenderTreeNode):
    soc_path: str = None

    def __init__(
        self,
        name: str,
        soc_path: str,
        parent: Node = None,
        children: List[Node] = None,
        **kwargs,
    ) -> None:
        """
        The node objects are part of a tree. Each node can access its children and it
        its parent, and has some custom attributes associated with it. To see more
        detailed documentation refer to the documentation of the anytree Python package

        :param name: Name of the node
        :type name: str
        :param soc_path: Path to the node in the SoC hiearchy
        :type soc_path: str
        :param parent: Parent of the node, defaults to None
        :type parent: Node, optional
        :param children: Children of the node, defaults to None
        :type children: List[Node], optional
        """
        super().__init__(name, parent, children, **kwargs)
        self.soc_path = soc_path

    def __hash__(self) -> int:
        return hash(self.soc_path)
