from typing import Callable, Dict, List, Tuple

from .enums import RunInfoEnum
from .data_reader import DataReader

from anytree import Node as RenderTreeNode
from anytree import RenderTree, PreOrderIter
from anytree.exporter import DotExporter
from anytree.search import findall
import pandas as pd


class Node(RenderTreeNode):
    soc_path: str = None
    seu_log: pd.DataFrame = None
    masking_series: pd.Series = None
    golden_log: pd.Series = None

    def __init__(self, name, parent=None, children=None, **kwargs):
        super().__init__(name, parent, children, **kwargs)

        self.soc_path = self._node_get_path_changer()

    def _node_get_path_changer(self) -> str:
        node_path = ""
        current_node = self

        while current_node.depth > 0:
            current_node = current_node.parent
            node_path = f"{current_node.name}.{node_path}"

        node_path += self.name

        return node_path

    def _add_data(self, data_reader: DataReader) -> None:
        seu_log = data_reader.get_seu_log_frame()
        masking_series = data_reader.get_masking_series()

        valid_indexes = list()

        for register in seu_log[RunInfoEnum.register.name].unique():
            if type(register) != str:
                continue

            if register.startswith(self.soc_path):
                index_at_reg = seu_log[RunInfoEnum.register.name] == register
                valid_indexes.extend(seu_log[index_at_reg].index)

        self.seu_log = seu_log.loc[valid_indexes]
        self.masking_series = masking_series.loc[valid_indexes]

        self.golden_log = data_reader.get_golden_log()


class RegisterTree:
    root: Node = None
    golden_log: pd.Series

    def __init__(self, file_path: str, data_reader: DataReader) -> None:
        self.golden_log = data_reader.get_golden_log()

        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Could not read file at {file_path}")
            print("Register tree will be empty.")
            print(e)

            return
        lines = [line.strip("\n") for line in lines]

        root_name = lines[0].split(".")[0]
        self.root = Node(root_name)

        for i, line in enumerate(lines):
            parts = line.split(".")
            current_node = self.root

            for part in parts[1:]:
                current_node_children_names = [
                    child.name for child in current_node.children
                ]
                if part not in current_node_children_names:
                    current_node = Node(part, parent=current_node)
                else:
                    current_node = [
                        child for child in current_node.children if child.name == part
                    ][0]

            current_node._add_data(data_reader)

    def run_analysis_on_all_nodes(
        self,
        func: Callable,
        start_node: Node = None,
        max_traversal_depth: int = -1,
        kwargs: Dict = dict(),
    ) -> List[Tuple[Node, None]]:
        if start_node is None:
            start_node = self.root

        result_list = []

        if max_traversal_depth == -1:
            iterator = PreOrderIter(start_node)
        else:
            start_depth = start_node.depth
            max_depth = start_depth + max_traversal_depth
            iterator = PreOrderIter(start_node, maxlevel=max_depth)

        for node in iterator:
            try:
                kwargs["data"] = node.seu_log
                kwargs["masking_series"] = node.masking_series
                kwargs["golden_log"] = self.golden_log
                result_list.append((node, func(**kwargs)))
            except Exception as e:
                print(f"Error in node {node.path}")
                print(f"Node is leaf: {node.is_leaf}")
                print(e)
                print()

        return result_list

    def get_node_by_path(self, path: str) -> Node:
        """
        Get a node by its path.

        Args:
            path (str): Path to the node.

        Returns:
            Node: The node at the given path.
        """
        path_parts = path.split(".")
        current_node = self.root

        for part in path_parts[1:]:
            current_node = [
                child for child in current_node.children if child.name == part
            ][0]

        return current_node

    def get_nodes_at_hierarchy_level(self, level: int) -> List[Node]:
        """
        Get all nodes at a given hierarchy level.

        Args:
            level (int): The level to get nodes from.

        Returns:
            List[Node]: A list of nodes at the given level.
        """
        return [node for node in PreOrderIter(self.root) if node.depth == level]


if __name__ == "__main__":
    print("This is a module.")
