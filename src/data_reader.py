from typing import List, Union
import os
from .fault_model import SeuDescription, HardError, SoftError, FaultDataModel
from .enums import CRCEnum


class DataReader:
    @classmethod
    def get_seu_fault_models(cls, data_dir_path: str) -> None:
        run_paths = [
            os.path.join(data_dir_path, path)
            for path in os.listdir(data_dir_path)
            if not path.endswith(".log")
        ]

        for run_path in run_paths:
            with open(os.path.join(run_path, "diff.log"), "r") as diff_file:
                diff_lines = diff_file.readlines()

            with open(os.path.join(run_path, "log.txt"), "r") as log_file:
                log_lines = log_file.readlines()

            seu_description = cls._get_seu_description(log_lines)
            soft_error = cls._get_soft_error(log_lines)

            _ = " "

    @classmethod
    def _get_soft_error(cls, log_lines: List[str]) -> SoftError:
        freq_value = int(
            float(
                [line for line in log_lines if line.startswith("CoreMark /")][0]
                .strip()
                .split(" ")[-1]
            )
            * 1e6
        )
        """
        seedcrc          : 0xe9f5
        [0]crclist       : 0xe714
        [0]crcmatrix     : 0x1fd7
        [0]crcstate      : 0x8e3a
        [0]crcfinal      : 0xe714
        """
        seedcrc = int(
            [line for line in log_lines if line.startswith("seedcrc")][0]
            .strip()
            .split(" ")[-1],
            16,  # hex
        )

        listcrc = int(
            [line for line in log_lines if line.startswith("[0]crclist")][0]
            .strip()
            .split(" ")[-1],
            16,  # Hex
        )

        matrixcrc = int(
            [line for line in log_lines if line.startswith("[0]crcmatrix")][0]
            .strip()
            .split(" ")[-1],
            16,  # Hex
        )

        statecrc = int(
            [line for line in log_lines if line.startswith("[0]crcstate")][0]
            .strip()
            .split(" ")[-1],
            16,  # Hex
        )

        finalcrc = int(
            [line for line in log_lines if line.startswith("[0]crcfinal")][0]
            .strip()
            .split(" ")[-1],
            16,  # Hex
        )

        crc_dict = {
            CRCEnum.seedcrc: seedcrc,
            CRCEnum.listcrc: listcrc,
            CRCEnum.matrixcrc: matrixcrc,
            CRCEnum.statecrc: statecrc,
            CRCEnum.finalcrc: finalcrc,
        }

        soft_error = SoftError(coremark_freq=freq_value, crc_value=crc_dict)

        return soft_error

    @classmethod
    def _get_seu_description(cls, log_lines: List[str]) -> SeuDescription:
        clock_cycle = int(
            [line for line in log_lines if line.startswith("Will flip bit at cycle")][0]
            .strip()
            .split(" ")[-2]
        )

        reg_value = (
            [line for line in log_lines if line.startswith("Forcing value for ")][0]
            .strip()
            .split(" ")[-1]
        )

        bit_numer = int(
            [line for line in log_lines if line.startswith("Fliping bit number")][0]
            .strip()
            .split(" ")[-1]
        )

        before_flip = int(
            [line for line in log_lines if line.startswith("Before flip")][0]
            .strip()
            .split(" ")[-1],
            16,  # hex
        )

        after_flip = int(
            [line for line in log_lines if line.startswith("After flip")][0]
            .strip()
            .split(" ")[-1],
            16,  # hex
        )

        seu_desccr = SeuDescription(
            bit_number=bit_numer,
            value_change=(before_flip, after_flip),
            clock_cycle=clock_cycle,
            register=reg_value,
        )

        return seu_desccr
