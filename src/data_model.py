from anytree import Node as RenderTreeNode, PreOrderIter
from anytree import findall as findall_nodes
import pandas as pd

from .firmwares import RunInfo, SeuRunInfo, InfoMapper
from .colorprint import ColorPrinter

from typing import Dict, List, Tuple, Union
from time import time as current_time
import os
import sys


class Node(RenderTreeNode):
    soc_path: str = None
    seu_log: pd.DataFrame = None
    masking_series: pd.Series = None
    golden_log: pd.Series = None

    def __init__(
        self,
        name,
        soc_path: str,
        seu_log: pd.DataFrame,
        masking_series: pd.Series,
        golden_log: pd.Series,
        parent=None,
        children=None,
        **kwargs,
    ):
        super().__init__(name, parent, children, **kwargs)

        run_is_on_node = seu_log[SeuRunInfo.register.name].apply(
            lambda x: x.startswith(soc_path)
        )
        node_run_idxs = seu_log[run_is_on_node].index

        self.soc_path = soc_path
        self.seu_log = seu_log.loc[node_run_idxs]
        self.masking_series = masking_series.loc[node_run_idxs]
        self.golden_log = golden_log


class RegisterTree:
    root: Node = None
    seu_log: pd.DataFrame = None
    masking_series: pd.Series = None
    golden_log: pd.Series = None
    no_reg_runs: List[str] = list()

    def __init__(
        self,
        data_directory: str,
        seu_log_name: str = "log.txt",
        golden_log_name: str = "golden_coremark_stdout.log",
        data_loading_timeout: int = 30,
    ) -> None:
        self._read_golden_file(data_directory, golden_log_name)
        self._read_viable_seu_logs(data_directory, seu_log_name, data_loading_timeout)
        self._create_register_tree()

    def get_node_by_path(self, path: str) -> Union[Node, None]:
        nodes = findall_nodes(
            self.root, filter_=lambda node: node.soc_path.startswith(path)
        )

        if len(nodes) == 0:
            return None

        node_depths = [node.depth for node in nodes]

        return nodes[node_depths.index(min(node_depths))]

    def get_nodes_at_hierarchy_level(self, level: int) -> List[Node]:
        """
        Get all nodes at a given hierarchy level.

        Args:
            level (int): The level to get nodes from.

        Returns:
            List[Node]: A list of nodes at the given level.
        """
        return [node for node in PreOrderIter(self.root) if node.depth == level]

    # TODO: Figure out how much logic in these methods can be moved outside of the class
    def _read_golden_file(self, data_directory: str, golden_log_name: str) -> None:
        path = os.path.join(data_directory, golden_log_name)
        try:
            with open(path, "r") as f:
                log_lines = f.readlines()
        except Exception as e:
            return None

        unfound_info = [info.name for info in RunInfo]
        golden_dict = dict()

        for line in log_lines:
            for info in unfound_info:
                match_pattern = RunInfo[info].value
                if match_pattern in line:
                    unfound_info.remove(info)
                    golden_dict[info] = InfoMapper.info_to_method_map[info](
                        line, match_pattern
                    )
                    break

        if len(unfound_info) > 0:
            ColorPrinter.print_fail(
                f"Could not find info in the golden log file: {unfound_info}"
            )
            sys.exit(1)

        self.golden_log = pd.Series(golden_dict)

    @ColorPrinter.print_func_time
    def _read_viable_seu_logs(
        self, data_directory: str, seu_log_name: str, data_loading_timout: int
    ) -> pd.DataFrame:
        viable_run_paths = self.__get_viable_runs(data_directory, seu_log_name)
        viable_run_paths = [
            os.path.join(path, seu_log_name) for path in viable_run_paths
        ]

        mask = dict()
        seu_log_frame = dict()

        start_time = current_time()
        check_every = 100

        for i, run_path in enumerate(viable_run_paths):
            run_name = run_path.split("/")[-2]

            try:
                res = self.__read_single_seu_log(run_path)
                if res is None:
                    self.no_reg_runs.append(run_name)
                    continue
                new_row, parsable = res
            except Exception as e:
                continue

            mask[run_name] = parsable
            seu_log_frame[run_name] = new_row

            if i % check_every != 0:
                continue
            if current_time() - start_time > data_loading_timout:
                print(
                    f"\nData loading timeout of {data_loading_timout} seconds reached. "
                    f"Stopping data loading.\n"
                )
                break

        self.masking_series = pd.Series(mask)
        self.seu_log = pd.DataFrame(seu_log_frame).T

    @ColorPrinter.print_func_time
    def _create_register_tree(self) -> None:
        # unique_regs = self.seu_log[SeuRunInfo.register.name][
        #     self.masking_series
        # ].unique()
        unique_regs = self.seu_log[SeuRunInfo.register.name].unique()

        _is_common_root = True
        _first_reg = unique_regs[0].split(".")[0]
        for reg in unique_regs:
            if reg.startswith(_first_reg):
                continue
            _is_common_root = False
            break
        assert _is_common_root, "All registers must have a common root"

        root_name = _first_reg
        self.root = Node(
            name=root_name,
            golden_log=self.golden_log,
            seu_log=self.seu_log,
            masking_series=self.masking_series,
            soc_path=root_name,
        )

        for register_number, reg_path in enumerate(unique_regs):
            parts = reg_path.split(".")
            current_node = self.root
            path_to_current_node = parts[0]

            for part in parts[1:]:
                path_to_current_node += f".{part}"
                current_node_children_names = [
                    child.name for child in current_node.children
                ]
                if part not in current_node_children_names:
                    current_node = Node(
                        name=part,
                        parent=current_node,
                        golden_log=self.golden_log,
                        seu_log=self.seu_log,
                        masking_series=self.masking_series,
                        soc_path=path_to_current_node,
                    )
                else:
                    current_node = [
                        child for child in current_node.children if child.name == part
                    ][0]

    def __get_viable_runs(self, data_directory: str, seu_log_name: str) -> List[str]:
        directories_in_data_dir = os.listdir(data_directory)
        directories_in_data_dir = [
            os.path.join(data_directory, dir)
            for dir in directories_in_data_dir
            if os.path.isdir(os.path.join(data_directory, dir))
        ]

        dirs_containing_seu_log = [
            dir for dir in directories_in_data_dir if seu_log_name in os.listdir(dir)
        ]

        return dirs_containing_seu_log

    def __read_single_seu_log(
        self, seu_log_path: str
    ) -> Union[Tuple[Dict[str, Union[str, int, float]], bool], None]:
        with open(seu_log_path, "r") as f:
            log_lines = f.readlines()

        unfound_info = []
        need_to_find = [info.name for info in SeuRunInfo]
        seu_log_dict = dict()
        for info in need_to_find:
            match_pattern = SeuRunInfo[info].value
            found_info = False
            for line in log_lines:
                if match_pattern in line:
                    found_info = True
                    seu_log_dict[info] = InfoMapper.info_to_method_map[info](
                        line, match_pattern
                    )

                if found_info:
                    break

            if not found_info:
                unfound_info.append(info)

        # older version of data passing. Replaced above
        # unfound_info = [info.name for info in SeuRunInfo]
        # seu_log_dict = dict()
        # for line in log_lines:
        #     for info in unfound_info:
        #         match_pattern = SeuRunInfo[info].value
        #         if match_pattern in line:
        #             unfound_info.remove(info)
        #             seu_log_dict[info] = InfoMapper.info_to_method_map[info](
        #                 line, match_pattern
        #             )
        #             break

        if SeuRunInfo.register.name in unfound_info:
            return None

        if len(unfound_info) > 0:
            for info in unfound_info:
                seu_log_dict[info] = None

            return seu_log_dict, False

        return seu_log_dict, True
