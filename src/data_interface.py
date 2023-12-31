from typing import List, Tuple, Union
import os

from anytree import findall as findall_nodes
import pandas as pd

from .run_info.run_info import RunInfo
from .data_parser import DataParser
from .colorprint import ColorPrinter as cp

from .analysis.structures.seu_log import SeuLog
from .analysis.structures.node import Node

# if you want to import optional data of some sort you need to change the import here
# and also create your own custom class in the structures fodler
# from .analysis.structures.optional_data.base_optional_data import (
#     BaseOptionalData as OptionalData,
# )
from .analysis.structures.optional_data.ibexhwsec_optional_data import (
    IbexHwsecOptionalData as OptionalData,
)


class DataInterface:
    run_info: RunInfo = None

    root: Node = None

    seu_log: SeuLog = None
    golden_log: pd.Series = None
    optional_data: OptionalData = None
    non_register_runs: List[str] = list()

    def __init__(self, run_info: RunInfo) -> None:
        """
        The data-structure the user should interface with in order to get data for
        analyses.

        The data interface has a reference to the configuartion object run_info, the
        root of the SoC-hiearchy tree, the full SeuLog describing all parsed runs,
        the golden run information, and the runs where we could not parse a register.

        :param run_info: Configuration object to use for parsing and interfacing with
        the data
        :type run_info: RunInfo
        """
        self.run_info = run_info

        print_start_read = False
        for option in [
            run_info.debug.percent_register_tree_populated,
        ]:
            print_start_read = print_start_read or option

        self.seu_log, self.non_register_runs = DataParser.read_seu_logs(run_info)
        self.golden_log = DataParser.read_golden_log(run_info)

        if print_start_read:
            cp.print_header("Building register tree")

        self._generate_register_tree(run_info)
        self.seu_log = SeuLog(self.seu_log)
        self.seu_log.name = self.root.name

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

        if run_info.data.read_optional:
            self.optional_data = DataParser.read_optional_logs(
                run_info, list(self.seu_log.index)
            )

    def get_node_by_path(self, path: str) -> Union[Node, None]:
        """
        Specify an SoC path, e.g. wrap.u_top.regfile.reg[2], and get the node
        corresponding to that path. If multiple nodes match this path the node with the
        smallest level is returned (i.e. the node with the shortest path in terms of
        levels)

        :param path: path to search the node by
        :type path: str
        :return: Node found by the search. If no Node is found returns None
        :rtype: Union[Node, None]
        """
        nodes = findall_nodes(
            self.root, filter_=lambda node: node.soc_path.startswith(path)
        )

        if len(nodes) == 0:
            return None

        if len(nodes) == 1:
            return nodes[0]

        node_depths = [node.depth for node in nodes]

        return nodes[node_depths.index(min(node_depths))]

    def get_node_by_name(self, name: str) -> Tuple[Node]:
        """
        Returns a tuple of all nodes where their name matches the name specified

        :param name: Name to search by
        :type name: str
        :return: Tuple of nodes found in the search
        :rtype: Tuple[Node]
        """
        return findall_nodes(self.root, filter_=lambda node: node.name == name)

    def get_seu_log_by_node(self, node: Node) -> SeuLog:
        """
        Use this method to query the full SeuLog for only data pertaining to a given
        node. All data which corresponds to this node, and its ancestors, is returned.

        :param node: Node to query the data with
        :type node: Node
        :return: Data pertaining to the specified node
        :rtype: SeuLog
        """
        data = self.seu_log.loc[
            self.seu_log.apply(
                lambda x: x["register"].startswith(node.soc_path), axis=1
            )
        ]

        data.name = node.name

        return data

    def get_openable_non_register_runs(self) -> List[str]:
        """
        Returns a list of runs which we can open, but where we cannot find the register
        entry. This is often because the run stalled, or had an illegal instruction.

        :return: List of openable runs where no register entry was parsed
        :rtype: List[str]
        """
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
        """
        Uses the VPI entry in the config file (*.ini) to generate the register tree.
        This tree represents the SoC hiearchy

        :param run_info: Configuration object
        :type run_info: RunInfo
        """
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
