from __future__ import annotations
from typing import Dict, List, Tuple, Union
from time import time as current_time
import os
import sys

from anytree import Node as RenderTreeNode
from anytree import findall as findall_nodes
import pandas as pd
import numpy as np

from .run_info import RunInfo
from .data_parser import DataParser
from .colorprint import ColorPrinter as cp
from .analysis import SeuLog


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
        super().__init__(name, parent, children, **kwargs)
        self.soc_path = soc_path


class DataInterface:
    run_info: RunInfo = None

    root: Node = None

    seu_log: SeuLog = None
    golden_log: pd.Series = None
    non_register_runs: List[str] = list()

    def __init__(self, run_info: RunInfo) -> None:
        self.run_info = run_info

        print_start_read = False
        for option in [
            run_info.debug.percent_register_tree_populated,
        ]:
            print_start_read = print_start_read or option

        self.seu_log, self.golden_log, self.non_register_runs = DataParser.read_data(
            run_info
        )

        if print_start_read:
            cp.print_header("Building register tree")

        self._generate_register_tree(run_info)

        if not run_info.debug.percent_register_tree_populated:
            if print_start_read:
                cp.print_header("Built register tree")
            return

        all_nodes = list(findall_nodes(self.root))
        all_nodes = [node for node in all_nodes if node.is_leaf]

        unpopulated_nodes = all_nodes.copy()
        hit_regs = list(self.seu_log.register.unique())

        for node in all_nodes:
            if node.soc_path in hit_regs:
                unpopulated_nodes.remove(node)

        unpop_percent = len(unpopulated_nodes) * 100 / len(all_nodes)
        cp.print_debug(f"  {unpop_percent:.2f}% of the register tree is unpopulated")
        cp.print_header("Built register tree")

    def get_node_by_path(self, path: str) -> Union[Node, None]:
        nodes = findall_nodes(
            self.root, filter_=lambda node: node.soc_path.startswith(path)
        )

        if len(nodes) == 0:
            return None

        node_depths = [node.depth for node in nodes]

        return nodes[node_depths.index(min(node_depths))]

    def get_node_by_name(self, name: str) -> Tuple[Node]:
        return findall_nodes(self.root, filter_=lambda node: node.name == name)

    def get_data_by_node(self, node: Node) -> SeuLog:
        data = self.seu_log.loc[
            self.seu_log.apply(
                lambda x: x["register"].startswith(node.soc_path), axis=1
            )
        ]

        data.name = node.name

        return data

    def get_openable_non_register_runs(self) -> List[str]:
        runs = list()
        for run_name in self.non_register_runs:
            try:
                with open(f"data/{run_name}/log.txt", "r") as f:
                    _ = f.readlines()

                runs.append(run_name)
            except:
                continue

        return runs

    def _generate_register_tree(self, run_info: RunInfo) -> None:
        vpi_path = os.path.join(os.getcwd(), run_info.data.directory, run_info.data.vpi)

        with open(vpi_path, "r") as f:
            register_paths = f.readlines()
        register_paths = [path.strip() for path in register_paths]

        root_path = register_paths[0].split(run_info.seu_metadata.register_delimiter)[0]
        self.root = Node(root_path, root_path)

        for reg_path in register_paths:
            parts = reg_path.split(run_info.seu_metadata.register_delimiter)
            current_node = self.root
            path_to_current_node = parts[0]

            for part in parts[1:]:
                path_to_current_node += f".{part}"
                current_node_children_names = [
                    child.name for child in current_node.children
                ]
                if part not in current_node_children_names:
                    current_node = Node(
                        name=part, parent=current_node, soc_path=path_to_current_node
                    )
                else:
                    current_node = [
                        child for child in current_node.children if child.name == part
                    ][0]
