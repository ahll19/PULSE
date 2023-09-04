from .enums import SeuDescriptionEnum, SoftErrorIndicatorEnum, LogInfoCastEnum

import pandas as pd
from numpy import nan as NaN

from time import time as current_time
from typing import Dict, List, Tuple, Union
import re
import os
import psutil


class DataReader:
    info_pattern_match_dict = {
        # Should be the text before each information piece we need
        SeuDescriptionEnum.injection_clock_cycle: "Will flip bit at cycle: ",
        SeuDescriptionEnum.register: "Forcing value for env.ibex_soc_wrap.ibex_soc_wrap.ibex_soc_i.",
        SeuDescriptionEnum.bit_number: "Fliping bit number: ",
        SeuDescriptionEnum.value_change_before: "Before flip: ",
        SeuDescriptionEnum.value_change_after: "After flip: ",
        SoftErrorIndicatorEnum.seedcrc: "seedcrc          : 0x",
        SoftErrorIndicatorEnum.listcrc: "[0]crclist       : 0x",
        SoftErrorIndicatorEnum.matrixcrc: "[0]crcmatrix     : 0x",
        SoftErrorIndicatorEnum.statecrc: "[0]crcstate      : 0x",
        SoftErrorIndicatorEnum.finalcrc: "[0]crcfinal      : 0x",
        SoftErrorIndicatorEnum.coremark_freq: "CoreMark / MHz: ",
    }

    info_pattern_type_dict = {
        SeuDescriptionEnum.injection_clock_cycle: LogInfoCastEnum.int,
        SeuDescriptionEnum.register: LogInfoCastEnum.str,
        SeuDescriptionEnum.bit_number: LogInfoCastEnum.int,
        SeuDescriptionEnum.value_change_before: LogInfoCastEnum.hex_to_int,
        SeuDescriptionEnum.value_change_after: LogInfoCastEnum.hex_to_int,
        SoftErrorIndicatorEnum.seedcrc: LogInfoCastEnum.hex_to_int,
        SoftErrorIndicatorEnum.listcrc: LogInfoCastEnum.hex_to_int,
        SoftErrorIndicatorEnum.matrixcrc: LogInfoCastEnum.hex_to_int,
        SoftErrorIndicatorEnum.statecrc: LogInfoCastEnum.hex_to_int,
        SoftErrorIndicatorEnum.finalcrc: LogInfoCastEnum.hex_to_int,
        SoftErrorIndicatorEnum.coremark_freq: LogInfoCastEnum.M_to_int,
    }

    @classmethod
    def get_data(
        cls, data_dir_path: str, max_ram_usage: float, max_time: float
    ) -> Tuple[pd.DataFrame, pd.Series]:
        run_paths = [
            os.path.join(data_dir_path, path) for path in os.listdir(data_dir_path)
        ]
        golden_reg_instr_log_path = ""
        golden_log_path = ""

        for i, path in enumerate(run_paths):
            if os.path.isdir(path):
                continue

            if path.endswith(".log"):
                golden_reg_instr_log_path = run_paths.pop(i)
            elif path.endswith(".txt"):
                golden_log_path = run_paths.pop(i)

        seu_results = dict()
        loop_check_mod = 100
        initial_ram_usage = psutil.virtual_memory().used / 10e9
        initial_time = current_time()

        for i, path in enumerate(run_paths):
            if i % loop_check_mod == 0:
                current_ram_usage = psutil.virtual_memory().used / 10e9
                if current_ram_usage - initial_ram_usage > max_ram_usage:
                    print(f"RAM usage exceeded {max_ram_usage} GB")
                    break

                curr_time = current_time()
                if curr_time - initial_time > max_time:
                    print(f"Time exceeded {max_time} seconds")
                    break

            res = cls._read_log_file(os.path.join(path, "log.txt"))
            if res is None:
                continue
            seu_results[path.split("/")[-1]] = res

        golden_log_results = cls._read_log_file(golden_log_path)
        golden_log_results.pop("hard error")

        return pd.DataFrame(seu_results).T, pd.Series(golden_log_results)

    @classmethod
    def _read_log_file(cls, log_path: str) -> Union[Dict[str, Union[str, int]], None]:
        not_found_lines = list(cls.info_pattern_match_dict.keys())
        _log_file_result = dict()

        try:
            with open(log_path, "r") as log_file:
                log_lines = log_file.readlines()
        except Exception as e:
            print(f"Error reading log file:")
            print(f"Log path:    {log_path}")
            print(f"exception:   {e}")

            return None

        for line in log_lines:
            for info_enum in not_found_lines:
                if cls.info_pattern_match_dict[info_enum] in line:
                    not_found_lines.remove(info_enum)

                    method = getattr(
                        cls, "_read_" + cls.info_pattern_type_dict[info_enum].name
                    )
                    try:
                        value = method(line, cls.info_pattern_match_dict[info_enum])
                        value = value if value is not None else NaN
                    except Exception as e:
                        not_found_lines.append(info_enum)
                        value = NaN
                        print(f"Error reading log file:")
                        print(f"method:      {method}")
                        print(f"line:        {line}")
                        print(f"Info:        {info_enum}")
                        print(f"Log path:    {log_path}")
                        print(f"exception:   {e}")

                    _log_file_result[info_enum.name] = value

        # Not a good solution, should be changed
        _log_file_result["hard error"] = len(not_found_lines) > 0

        return _log_file_result

    @classmethod
    def _read_int(cls, line: str, rm_str: str) -> int:
        stripped = line.replace(rm_str, "")
        numbers_only = re.findall(r"\d+", stripped)
        result = int(numbers_only[0])

        return result

    @classmethod
    def _read_str(cls, line: str, rm_str: str) -> str:
        result = line.split(rm_str)[-1].strip("\n")

        return result

    @classmethod
    def _read_hex_to_int(cls, line: str, rm_str: str) -> int:
        stripped = line.replace(rm_str, "").strip("\n")
        hex_only = re.findall(r"[0-9a-fA-F]+", stripped)
        result = int(hex_only[0], 16)

        return result

    @classmethod
    def _read_M_to_int(cls, line: str, rm_str: str) -> int:
        stripped = line.replace(rm_str, "")
        decimal_only = re.findall(r"\.\d+", stripped)

        if len(decimal_only) == 0:
            decimal_only = stripped[0]

            if decimal_only not in list("0123456789"):
                return NaN

        result = int(float(decimal_only[0]) * 10e6)

        return result
