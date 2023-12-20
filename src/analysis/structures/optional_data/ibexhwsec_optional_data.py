from typing import Dict, Tuple
import re

import pandas as pd

from .base_optional_data import BaseOptionalData, RunInfo


class IbexHwsecOptionalData(BaseOptionalData):
    alert_val_name = "Alert value"
    alert_cyc_name = "Alert cycle"
    alert_val_match_string = "Alert signal raised: "
    alert_cyc_match_string = "Alert cycle: "

    optional_datas: Dict[str, pd.DataFrame] = dict()

    def __init__(self, run_info: RunInfo) -> None:
        super().__init__(run_info)

    def _read_optional_log(self, run_path: str) -> None:
        try:
            with open(run_path, "r") as f:
                log_lines = f.readlines()
        except UnicodeDecodeError as e:
            return None

        result = dict()
        register: str = None
        reg = self.run_info.seu_metadata.register

        matched = False
        not_found_reg = True
        for i, line in enumerate(log_lines):
            # This loop assumes that the alert val will always come before the cycle
            if matched:
                matched = False
                continue

            if not_found_reg:
                if reg in line:
                    not_found_reg = False
                    register = line.split(reg)[1].strip(" \n\t[]0123456789")

            if not (self.alert_val_match_string in line):
                continue

            matched = True

            res = self.__parse_cycles((line, log_lines[i + 1]))
            result[len(result)] = res

        if register is None or len(result) == 0:
            return None

        self.optional_datas[run_path.split("/")[-2]] = pd.DataFrame.from_dict(
            result, orient="index"
        )

    def get_data_by_run(self, run: str) -> pd.DataFrame:
        try:
            return self.optional_datas[run]
        except KeyError:
            return None

    def __parse_cycles(self, lines: Tuple[str, str]) -> Dict[str, int]:
        val = list(map(int, re.findall(r"\d+", lines[0])))[0]
        cyc = list(map(int, re.findall(r"\d+", lines[1])))[0]

        return {self.alert_val_name: val, self.alert_cyc_name: cyc}
