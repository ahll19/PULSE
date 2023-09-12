from .data_reader_mappings import ReaderMapper
from .enums import RunInfoEnum, GoldenRunInfoEnum

from typing import Dict, List, Tuple, Union
from time import time as current_time
from psutil import virtual_memory
import os

import pandas as pd


class DataReader:
    """
    Though the naming doesn't quite make match, in the code we denote files a follows:
        - a 'log' file as a file containing printed logs from a given simulation.
        - a 'instr' file containing the instrs run during a simulation.
    """

    # TODO: possible to add -1 to ram and timer to disable them

    # Information to be accessed by the user
    seu_log_frame: pd.DataFrame = None
    masking_series: pd.Series = None
    golden_instr_log: pd.DataFrame = None
    golden_log: pd.Series = None

    # Used for reading the files. Should not be accessed directly by user
    _mapper: ReaderMapper = ReaderMapper()
    _golden_wanted_info = [num.name for num in GoldenRunInfoEnum]
    _seu_wanted_info = [num.name for num in RunInfoEnum]

    # User specified settings
    data_dir_path: str = None
    max_ram_usage: float = None
    timeout_time: float = None
    check_every: int = None
    gold_instr_file_name: str = None
    gold_log_file_name: str = None
    seu_instr_file_name: str = None
    seu_log_file_name: str = None

    def __init__(
        self,
        data_directory_path: str,
        max_ram_usage: float = 2,
        timeout_time: float = 30,
        check_every: int = 50,
        gold_instr_file_name: str = "golden.log",
        gold_log_file_name: str = "golden.txt",
        seu_instr_file_name: str = "diff.log",
        seu_log_file_name: str = "log.txt",
    ) -> None:
        self.data_dir_path = data_directory_path
        self.max_ram_usage = max_ram_usage
        self.timeout_time = timeout_time
        self.check_every = check_every
        self.gold_instr_file_name = gold_instr_file_name
        self.gold_log_file_name = gold_log_file_name
        self.seu_instr_file_name = seu_instr_file_name
        self.seu_log_file_name = seu_log_file_name

        self._check_path_and_directory(data_directory_path)

        print("Loading data...")
        t1 = current_time()
        exeited_early = self.load_data()
        t2 = current_time()
        if exeited_early:
            print("Data loading exited early due to settings limit.")

        print(f"Data loaded in {t2 - t1:.2f} seconds.")

    def load_data(self) -> bool:
        """
        Loads the data from the specified directory. Only call this if you need to
        reload the data from the directory.

        Returns:
            bool: Returns True if the timeout or ram limit was hit, False otherwise.
        """
        run_dirs = [
            dir
            for dir in os.listdir(self.data_dir_path)
            if not (dir in [self.gold_instr_file_name, self.gold_log_file_name])
            and os.path.isdir(os.path.join(self.data_dir_path, dir))
        ]
        seu_log_paths = [
            os.path.join(self.data_dir_path, dir, self.seu_log_file_name)
            for dir in run_dirs
        ]
        seu_instr_paths = [
            os.path.join(self.data_dir_path, dir, self.seu_instr_file_name)
            for dir in run_dirs
        ]
        golden_log_path = os.path.join(self.data_dir_path, self.gold_log_file_name)
        golden_instr_path = os.path.join(self.data_dir_path, self.gold_instr_file_name)

        self.golden_log = self._read_golden_log_file(golden_log_path)
        self.golden_instr_log = self._read_golden_instr_log_file(golden_instr_path)

        seu_log_frame_dict = dict()
        masking_dict = dict()

        hit_ram_limit = False
        hit_time_limit = False

        initial_mem_usage = virtual_memory().used / 10e9
        t0 = current_time()

        for i, (run_name, log_path, instr_path) in enumerate(
            zip(run_dirs, seu_log_paths, seu_instr_paths)
        ):
            got_all, new_log_row = self._read_seu_log_file(log_path)
            if new_log_row is not None:
                seu_log_frame_dict[run_name] = new_log_row
                masking_dict[run_name] = got_all

            if i % self.check_every == 0:
                current_mem_usage = virtual_memory().used / 10e9
                if current_mem_usage - initial_mem_usage > self.max_ram_usage:
                    print(f"RAM usage exceeded {self.max_ram_usage} GB")
                    hit_ram_limit = True
                    break

                t1 = current_time()
                if t1 - t0 > self.timeout_time:
                    print(f"Load time exceeded {self.timeout_time} seconds")
                    hit_time_limit = True
                    break

        self.seu_log_frame = pd.DataFrame(seu_log_frame_dict).T
        self.masking_series = pd.Series(masking_dict)

        return hit_ram_limit or hit_time_limit

    def _read_seu_log_file(
        self, log_path: str
    ) -> Tuple[bool, Dict[str, Union[str, int, float, None]]]:
        try:
            with open(log_path, "r") as f:
                log_lines = f.readlines()
        except Exception as e:
            print(f"Could not read log file at {log_path}")
            print(e)
            return False, None

        unfound_info = self._seu_wanted_info.copy()
        new_row = dict()

        for line in log_lines:
            for info in unfound_info:
                match_pattern = self._mapper.info_to_pattern_map[info]
                if match_pattern in line:
                    unfound_info.remove(info)
                    new_row[info] = self._mapper.info_to_method_map[info](
                        line, match_pattern
                    )
                    break

        if len(unfound_info) > 0:
            return False, new_row
        else:
            return True, new_row

    def _read_golden_log_file(self, log_path: str) -> pd.Series:
        try:
            with open(log_path, "r") as f:
                log_lines = f.readlines()
        except Exception as e:
            print(f"Could not read log file at {log_path}")
            print(e)
            return None

        unfound_info = self._golden_wanted_info.copy()
        new_row = dict()

        for line in log_lines:
            for info in unfound_info:
                match_pattern = self._mapper.info_to_pattern_map[info]
                if match_pattern in line:
                    unfound_info.remove(info)
                    new_row[info] = self._mapper.info_to_method_map[info](
                        line, match_pattern
                    )
                    break

        if len(unfound_info) > 0:
            print("Could not find the following info in the golden log file:")
            print(unfound_info)
            return None
        else:
            return pd.Series(new_row)

    def _read_golden_instr_log_file(self, log_path: str) -> pd.DataFrame:
        # TODO: Fix instruction mapping format before continuing
        return None

    def _read_seu_instr_log_file(self, log_path: str) -> None:
        # TODO: Figure out the best format to save this in
        return None

    def _check_path_and_directory(self, path: str) -> None:
        if not os.path.isdir(path):
            raise ValueError(f"Path {path} is not a directory.")

        dir_and_files_in_path = os.listdir(path)
        if not (self.gold_instr_file_name in dir_and_files_in_path):
            raise ValueError(f"Path {path} does not contain a golden instr file.")
        if not (self.gold_log_file_name in dir_and_files_in_path):
            raise ValueError(f"Path {path} does not contain a golden log file.")

    def get_golden_log(self) -> pd.Series:
        return self.golden_log

    def get_seu_log_frame(self) -> pd.DataFrame:
        return self.seu_log_frame

    def get_masking_series(self) -> pd.Series:
        return self.masking_series

    # def get_golden_instr_log(self) -> pd.DataFrame:
    #     return self.golden_instr_log
