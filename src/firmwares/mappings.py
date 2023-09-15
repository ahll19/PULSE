import numpy as np

import re


class MappingMethods:
    @staticmethod
    def read_int(line: str, rm_str: str) -> int:
        stripped = line.replace(rm_str, "")
        numbers_only = re.findall(r"\d+", stripped)
        result = int(numbers_only[0])

        return result

    @staticmethod
    def read_str(line: str, rm_str: str) -> str:
        result = line.split(rm_str)[-1].strip("\n")

        return result

    @staticmethod
    def read_hex_to_int(line: str, rm_str: str) -> int:
        stripped = line.replace(rm_str, "").strip("\n")
        hex_only = re.findall(r"[0-9a-fA-F]+", stripped)
        result = int(hex_only[0], 16)

        return result

    @staticmethod
    def read_M_to_int(line: str, rm_str: str) -> int:
        # used for mapping megaherz to int: e.g. 2.464051
        stripped = line.replace(rm_str, "")
        decimal_only = re.findall(r"\.\d+", stripped)

        if len(decimal_only) == 0:
            decimal_only = stripped[0]

            if decimal_only not in list("0123456789"):
                return np.NaN

        result = int(float(decimal_only[0]) * 10e6)

        return result
