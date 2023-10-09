from .configs import Config

from anytree import Node

import os
import sys


class Node:
    soc_path: str = None

    def __init__(
        self,
        soc_path: str,
        parent=None,
        children=None,
    ) -> None:
        pass


class DataStructure:
    config: Config = None

    def __init__(self, config: Config) -> None:
        if not config.config_is_set:
            raise ValueError("Config is not set. Run Config.set_config() first.")

        self.config = config

        self.read_vpi_file()

    def read_vpi_file(self):
        assert os.path.isfile(
            self.config.VPI_TXT_PATH
        ), f"File not found at {self.config.VPI_TXT_PATH}, check config file"

        regs = list()
        with open(self.config.VPI_TXT_PATH, "r") as f:
            regs = f.readlines()

        _is_common_root = True
        _first_reg = regs[0].split(".")[0]
        for reg in unique_regs:
            if reg.startswith(_first_reg):
                continue
            _is_common_root = False
            break
        assert _is_common_root, "All registers must have a common root"
