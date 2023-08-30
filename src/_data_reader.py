from typing import Dict, List
import os
from .fault_model import SeuDescription, HardError, SoftError, FaultDataModel
from .enums import CRCEnum, ExitValueEnum


class DataReader:
    @classmethod
    def get_golden_fault_model(cls, golden_log_path: str) -> FaultDataModel:
        raise NotImplementedError("This is probably over engineered")

    @classmethod
    def get_seu_fault_models(cls, data_dir_path: str) -> Dict[str, FaultDataModel]:
        run_paths = [
            os.path.join(data_dir_path, path)
            for path in os.listdir(data_dir_path)
            if (not path.endswith(".log") and not path.endswith(".txt"))
        ]

        fault_models = dict()

        wrong_counter = 0
        for i, run_path in enumerate(run_paths):
            with open(os.path.join(run_path, "diff.log"), "r") as diff_file:
                diff_lines = diff_file.readlines()

            with open(os.path.join(run_path, "log.txt"), "r") as log_file:
                log_lines = log_file.readlines()

            try:
                seu_description = cls._get_seu_description(log_lines)
                soft_error = cls._get_soft_error(log_lines)
                hard_error = cls._get_hard_errors(log_lines)
            except:
                wrong_counter += 1
                continue

            fault_data_model = FaultDataModel(
                seu_description=seu_description,
                soft_error=soft_error,
                hard_error=hard_error,
            )

            fault_models[run_path] = fault_data_model

        print(f"Wrong counter: {wrong_counter}")
        print(f"This is ~{wrong_counter / len(run_paths) * 100:.1f}% of the data")

        return fault_models

    @classmethod
    def _get_hard_errors(cls, log_lines: List[str]) -> HardError:
        exit_vals = [
            int(exit_line.strip().split(" ")[-1])
            for exit_line in [
                line
                for line in log_lines
                if line.startswith("Program exited with value")
                or line.startswith("Exit val")
            ]
        ]

        # Could be expanded with other exit values for more information, but for now we
        # only care about the normal exit value. If it is not the only one we say we got
        # a bad exit
        good_exits_only = len(exit_vals) > 0
        for exit_val in exit_vals:
            if not good_exits_only:
                break

            good_exits_only &= exit_val == ExitValueEnum.normal_exit.value

        # hard-coded for ease of use right now
        cpu_stall = False

        hard_error = HardError(cpu_stall=cpu_stall, bad_exit=not good_exits_only)

        return hard_error

    @classmethod
    def _get_soft_error(cls, log_lines: List[str]) -> SoftError:
        # Consider instruction / reg log diff in future

        # tmp fix, redo with smarter code
        freq_value = int(
            float(
                [line for line in log_lines if line.startswith("CoreMark /")][0]
                .strip()
                .split(" ")[-1]
            )
            * 1e6
        )

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
            CRCEnum.seed: seedcrc,
            CRCEnum.list: listcrc,
            CRCEnum.matrix: matrixcrc,
            CRCEnum.state: statecrc,
            CRCEnum.final: finalcrc,
        }

        soft_error = SoftError(coremark_freq=freq_value, crc_value=crc_dict)

        return soft_error

    @classmethod
    def _get_seu_description(cls, log_lines: List[str]) -> SeuDescription:
        clock_cycle = int(
            [line for line in log_lines if line.startswith("Will flip bit at cycle")][0]
            .strip()
            .split(" ")[-2]
            .split(".")[0]  # sometimes decimal is present. Shouldnt be, temp fix
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
