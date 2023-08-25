from typing import Dict, List, Tuple
import pandas as pd
import os
from time import time as curr_time
import re


class RunData:
    """
    Expected structure of a run (example):
        data
    ├── golden.log
    ├── seu_2023-08-25_07-34-13.396916
    │   ├── diff.log
    │   └── log.txt
    ├── seu_2023-08-25_07-34-13.398265
    │   ├── diff.log
    │   └── log.txt
    ├── seu_2023-08-25_07-34-13.400563
    │   ├── diff.log
    │   └── log.txt
    └── seu_2023-08-25_07-34-13.434978
        ├── diff.log
        └── log.txt

    Class does not accept other structures right now...
    """

    _run_path: str = None
    _golden_path: str = None
    _seu_injection_paths: Dict[str, Dict[str, str]] = dict()

    golden_run: pd.DataFrame = None
    seu_results: Dict[str, Dict[str, List[str]]] = dict()

    def __init__(
        self, run_path: str, golden_n_lines_max: int, golden_read_timeout: int
    ) -> None:
        # This way of handling the data is very annoying, and should be changed
        # The headers dont really describe the instructions/registers
        self.__path_handling(run_path=run_path)
        self.__handle_golden(
            golden_n_lines_max=golden_n_lines_max,
            golden_read_timeout=golden_read_timeout,
        )
        self.__handle_seu()

    def __handle_seu(self):
        for _run_path, type_dict in self._seu_injection_paths.items():
            self.seu_results[_run_path] = dict()
            for type, name in type_dict.items():
                with open(_run_path + name, "r") as f:
                    lines = f.readlines()

                self.seu_results[_run_path][type] = lines

    def __handle_golden(self, golden_n_lines_max: int, golden_read_timeout: int):
        lines = []
        n_read_lines = 0
        start_time = curr_time()

        with open(self._golden_path, "r") as golden_file:
            while (
                curr_time() < start_time + golden_read_timeout
                and n_read_lines < golden_n_lines_max
            ):
                line = golden_file.readline()
                if line == "":
                    break

                lines.append(line)

        lines = [re.split("\t| and ", line) for line in lines]
        header = lines.pop(0)

        self.golden_run = pd.DataFrame(lines, columns=header)

    def __path_handling(self, run_path: str):
        if not run_path.endswith("/"):
            run_path += "/"

        self._run_path = run_path
        self._golden_path = run_path + "golden.log"
        seu_run_names = [
            run_path + name for name in os.listdir(run_path) if name != "golden.log"
        ]

        for run in seu_run_names:
            self._seu_injection_paths[run] = {"diff": "/diff.log", "log": "/log.txt"}

        # Make sure runs actually exist
        assert os.path.isdir(self._run_path), "Run path not found"
        assert os.path.isfile(self._golden_path), "Golden file not found"
        for path, type in self._seu_injection_paths.items():
            assert os.path.isfile(path + type["diff"]), "error when looking for diff"
            assert os.path.isfile(path + type["log"]), "error when looking for log"


if __name__ == "__main__":
    pass
