import os
from typing import Dict, List, Tuple, Union
from .enums import InfoEnum, InfoCastEnum
import pandas as pd
from numpy import nan as NaN
import re


class DataReader:
    info_pattern_match_dict = {
        # Should be the text before each information piece we need
        InfoEnum.injection_clock_cycle: "Will flip bit at cycle: ",
        InfoEnum.register: "Forcing value for ",
        InfoEnum.bit_number: "Fliping bit number: ",
        InfoEnum.value_change_before: "Before flip: ",
        InfoEnum.value_change_after: "After flip: ",
        InfoEnum.seedcrc: "seedcrc          : 0x",
        InfoEnum.listcrc: "[0]crclist       : 0x",
        InfoEnum.matrixcrc: "[0]crcmatrix     : 0x",
        InfoEnum.statecrc: "[0]crcstate      : 0x",
        InfoEnum.finalcrc: "[0]crcfinal      : 0x",
        InfoEnum.coremark_freq: "CoreMark / MHz: ",
    }

    info_pattern_type_dict = {
        InfoEnum.injection_clock_cycle: InfoCastEnum.int,
        InfoEnum.register: InfoCastEnum.str,
        InfoEnum.bit_number: InfoCastEnum.int,
        InfoEnum.value_change_before: InfoCastEnum.hex_to_int,
        InfoEnum.value_change_after: InfoCastEnum.hex_to_int,
        InfoEnum.seedcrc: InfoCastEnum.hex_to_int,
        InfoEnum.listcrc: InfoCastEnum.hex_to_int,
        InfoEnum.matrixcrc: InfoCastEnum.hex_to_int,
        InfoEnum.statecrc: InfoCastEnum.hex_to_int,
        InfoEnum.finalcrc: InfoCastEnum.hex_to_int,
        InfoEnum.coremark_freq: InfoCastEnum.M_to_int,
    }

    info_method_dict = {
        InfoEnum.injection_clock_cycle: "_read_int",
        InfoEnum.register: "_read_str",
        InfoEnum.bit_number: "_read_int",
        InfoEnum.value_change_before: "_read_hex_to_int",
        InfoEnum.value_change_after: "_read_hex_to_int",
        InfoEnum.seedcrc: "_read_hex_to_int",
        InfoEnum.listcrc: "_read_hex_to_int",
        InfoEnum.matrixcrc: "_read_hex_to_int",
        InfoEnum.statecrc: "_read_hex_to_int",
        InfoEnum.finalcrc: "_read_hex_to_int",
        InfoEnum.coremark_freq: "_read_M_to_int",
    }

    @classmethod
    def get_data(cls, data_dir_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
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
        for path in run_paths:
            seu_results[path.split("/")[-1]] = cls._read_log_file(
                os.path.join(path, "log.txt")
            )

        golden_log_results = cls._read_log_file(golden_log_path)

        return pd.DataFrame(seu_results).T, pd.Series(golden_log_results)

    @classmethod
    def _read_log_file(cls, log_path: str) -> Dict[str, Union[str, int]]:
        not_found_lines = list(cls.info_pattern_match_dict.keys())
        _log_file_result = dict()

        with open(log_path, "r") as log_file:
            log_lines = log_file.readlines()

        for line in log_lines:
            for info_enum in not_found_lines:
                if cls.info_pattern_match_dict[info_enum] in line:
                    not_found_lines.remove(info_enum)

                    method = getattr(cls, cls.info_method_dict[info_enum])
                    try:
                        value = method(line, cls.info_pattern_match_dict[info_enum])
                        value = value if value is not None else NaN
                    except Exception as e:
                        value = NaN
                        print(f"Error reading log file:")
                        print(f"    method {method}")
                        print(f"    line {line}")
                        print(f"    pattern {cls.info_pattern_match_dict[info_enum]}")
                        print(f"    enum {info_enum}")
                        print(f"    exception {e}")

                    _log_file_result[info_enum.name] = value

        if len(not_found_lines) > 0:
            # Here we should handle hard errors
            _ = ""

        return _log_file_result

    @classmethod
    def _read_int(cls, line: str, rm_str: str) -> int:
        stripped = line.replace(rm_str, "")
        numbers_only = re.findall(r"\d+", stripped)
        result = int(numbers_only[0])

        return result

    @classmethod
    def _read_str(cls, line: str, rm_str: str) -> str:
        result = line.replace(rm_str, "").strip("\n")

        return result

    @classmethod
    def _read_hex_to_int(cls, line: str, rm_str: str) -> int:
        stripped = line.replace(rm_str, "")
        hex_only = re.findall(r"[0-9a-fA-F]+", stripped)
        result = int(hex_only[0], 16)

        return result

    @classmethod
    def _read_M_to_int(cls, line: str, rm_str: str) -> int:
        stripped = line.replace(rm_str, "")
        decimal_only = re.findall(r"\.\d+", stripped)
        result = int(float(decimal_only[0]) * 10e6)

        return result
