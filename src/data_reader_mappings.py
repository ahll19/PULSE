from .enums import GoldenRunInfoEnum, RunInfoEnum

import numpy as np

import re
from typing import Dict, Callable


class ReaderMapper:
    info_to_pattern_map: Dict[RunInfoEnum, str]
    info_to_method_map: Dict[RunInfoEnum, Callable]

    def __init__(self) -> None:
        # TODO: check that the maps are exhaustive of the RunInfoEnum
        self.info_to_pattern_map = {
            RunInfoEnum.injection_cycle.name: "Will flip bit at cycle: ",
            RunInfoEnum.register.name: "Forcing value for env.ibex_soc_wrap.",
            RunInfoEnum.bit_number.name: "Fliping bit number: ",
            RunInfoEnum.value_before.name: "Before flip: ",
            RunInfoEnum.value_after.name: "After flip: ",
            RunInfoEnum.seed_crc.name: "seedcrc          : 0x",
            RunInfoEnum.list_crc.name: "[0]crclist       : 0x",
            RunInfoEnum.matrix_crc.name: "[0]crcmatrix     : 0x",
            RunInfoEnum.state_crc.name: "[0]crcstate      : 0x",
            RunInfoEnum.final_crc.name: "[0]crcfinal      : 0x",
            RunInfoEnum.coremark_score.name: "CoreMark / MHz: ",
        }
        self.info_to_method_map = {
            RunInfoEnum.injection_cycle.name: self._read_int,
            RunInfoEnum.register.name: self._read_str,
            RunInfoEnum.bit_number.name: self._read_int,
            RunInfoEnum.value_before.name: self._read_hex_to_int,
            RunInfoEnum.value_after.name: self._read_hex_to_int,
            RunInfoEnum.seed_crc.name: self._read_hex_to_int,
            RunInfoEnum.list_crc.name: self._read_hex_to_int,
            RunInfoEnum.matrix_crc.name: self._read_hex_to_int,
            RunInfoEnum.state_crc.name: self._read_hex_to_int,
            RunInfoEnum.final_crc.name: self._read_hex_to_int,
            RunInfoEnum.coremark_score.name: self._read_M_to_int,
        }

    def _read_int(self, line: str, rm_str: str) -> int:
        stripped = line.replace(rm_str, "")
        numbers_only = re.findall(r"\d+", stripped)
        result = int(numbers_only[0])

        return result

    def _read_str(self, line: str, rm_str: str) -> str:
        result = line.split(rm_str)[-1].strip("\n")

        return result

    def _read_hex_to_int(self, line: str, rm_str: str) -> int:
        stripped = line.replace(rm_str, "").strip("\n")
        hex_only = re.findall(r"[0-9a-fA-F]+", stripped)
        result = int(hex_only[0], 16)

        return result

    def _read_M_to_int(self, line: str, rm_str: str) -> int:
        stripped = line.replace(rm_str, "")
        decimal_only = re.findall(r"\.\d+", stripped)

        if len(decimal_only) == 0:
            decimal_only = stripped[0]

            if decimal_only not in list("0123456789"):
                return np.NaN

        result = int(float(decimal_only[0]) * 10e6)

        return result
