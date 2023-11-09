from typing import Dict, List, Tuple
from time import time as current_time
import os
import sys

import pandas as pd
import numpy as np
from tqdm import tqdm

from .run_info.run_info import RunInfo
from .colorprint import ColorPrinter as cp


class DataParser:
    @classmethod
    def read_data(cls, run_info: RunInfo) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
        """
        Method called by the data interface to get all data specified by the config

        :param run_info: Configuration object
        :type run_info: RunInfo
        :return: the seu_log, golden_run, non_register_run objects saved by the data-
        interface
        :rtype: Tuple[pd.DataFrame, pd.Series, List[str]]
        """
        golden_log = cls._read_golden_log(run_info)
        seu_log, non_register_runs = cls._read_all_seu_logs(run_info)

        return seu_log, golden_log, non_register_runs

    @classmethod
    def _read_all_seu_logs(cls, run_info: RunInfo) -> Tuple[pd.DataFrame, List[str]]:
        """
        Finds all runs in the data-directory, and iterates through them to read all
        runs. Note this method calls the _read_single_seu_log() method to parse single
        logs.

        :param run_info: Configuration object
        :type run_info: RunInfo
        :return: Returns the parsed logs, and a list of runs with no registers
        :rtype: Tuple[pd.DataFrame, List[str]]
        """
        err_str = "Error string not set in run_info\n"
        err_str += f"Check {run_info.path} SEU_METADATA section for entry named "
        err_str += "register."

        if not hasattr(run_info.seu_metadata, "register"):
            print(err_str)
            print("Exiting...")
            sys.exit(1)

        run_logs = dict()
        non_reg_runs = list()

        info_to_find = run_info.seu_metadata.entries.copy()
        info_to_find += run_info.comparison_data.entries.copy()
        if run_info.data.read_optional:
            if not run_info.optional_data.entries:
                print(err_str)
                print("Exiting...")
                sys.exit(1)
            optional_find = run_info.optional_data.entries.copy()

        curr_time = current_time()
        timeout = run_info.data.timeout
        should_timeout = timeout != -1
        n_failed_reads = 0

        print_start_read = False
        for option in [
            run_info.debug.percent_failed_reads,
            run_info.debug.error_utf_parsing,
            run_info.debug.loading_bar_on_data_parsing,
        ]:
            print_start_read = print_start_read or option
        if print_start_read:
            cp.print_header("Parsing SEU logs...")

        _iter = os.listdir(os.path.join(os.getcwd(), run_info.data.directory))
        iter = tqdm(_iter) if run_info.debug.loading_bar_on_data_parsing else _iter

        for run in iter:
            if should_timeout:
                if current_time() - curr_time > timeout:
                    print(f"Timed out after {timeout} seconds")
                    break

            dir_path = path = os.path.join(os.getcwd(), run_info.data.directory, run)
            if not os.path.isdir(dir_path):
                continue

            if not run_info.data.seu in os.listdir(dir_path):
                continue

            path = os.path.join(
                os.getcwd(), run_info.data.directory, run, run_info.data.seu
            )
            log_dict, found_reg, failed_read = cls._read_single_seu_log(
                run_info, path, info_to_find
            )

            n_failed_reads += failed_read

            if found_reg:
                if run_info.data.read_optional:
                    optional_log_dict, found_all_optionals, _ = cls._read_optional_log(
                        run_info, path, optional_find
                    )
                    log_dict |= optional_log_dict  # append optional dict
                run_logs[run] = log_dict
            else:
                non_reg_runs.append(run)

        if run_info.debug.percent_failed_reads:
            cp.print_bold_debug(
                f"  Parsed {len(run_logs)} logs, percent failed reads: {n_failed_reads / len(run_logs) * 100:.2f}%"
            )

        if print_start_read:
            cp.print_header("Done parsing SEU logs")

        return pd.DataFrame(run_logs).T, non_reg_runs

    @classmethod
    def _read_optional_log(
        cls, run_info: RunInfo, path: str, info_to_find: List[str]
    ) -> Tuple[Dict[str, str], bool, int]:
        seu_log_dict = dict()
        unfound_info = info_to_find.copy()

        try:
            with open(path, "r") as f:
                lines = f.readlines()
        except UnicodeDecodeError as e:
            if run_info.debug.error_utf_parsing:
                cp.print_debug(f"  Could not read {path}")
                cp.print_debug("  " + str(e))
            return None, False, 1

        for info in info_to_find:
            # This logic has to change if we decide to do non-binary comparisons
            found_info = False
            if hasattr(run_info.optional_data, info):
                match_pattern = getattr(run_info.optional_data, info)
            else:
                return None, False, 1

            for line in lines:
                if match_pattern in line:
                    seu_log_dict[info] = line.split(match_pattern)[1].strip()
                    unfound_info.remove(info)
                    found_info = True
                    break

            if not found_info:
                seu_log_dict[info] = 0

        return seu_log_dict, not bool(unfound_info), 0

    @classmethod
    def _read_single_seu_log(
        cls, run_info: RunInfo, path: str, info_to_find: List[str]
    ) -> Tuple[Dict[str, str], bool, int]:
        """
        Parses a single seu_log.

        Uses the configuration object to check which information has to be parsed, and
        if this information is not found the method exits in a way that the
        _read_all_seu_logs() methods handles

        :param run_info: Configuration object
        :type run_info: RunInfo
        :param path: Path for the individual run
        :type path: str
        :param info_to_find: A list containing what information should be found by the
        parser.
        :type info_to_find: List[str]
        :return: A dictionary containing the found information, a boolean on whether the
        parsing was succesful, and an exit code (0=openable file, 1=unopanable file)
        :rtype: Tuple[Dict[str, str], bool, int]
        """
        seu_log_dict = dict()
        unfound_info = info_to_find.copy()

        try:
            with open(path, "r") as f:
                lines = f.readlines()
        except UnicodeDecodeError as e:
            if run_info.debug.error_utf_parsing:
                cp.print_debug(f"  Could not read {path}")
                cp.print_debug("  " + str(e))
            return None, False, 1

        for info in info_to_find:
            # This logic has to change if we decide to do non-binary comparisons
            found_info = False
            if hasattr(run_info.seu_metadata, info):
                match_pattern = getattr(run_info.seu_metadata, info)
            else:
                match_pattern = getattr(run_info.comparison_data, info)

            for line in lines:
                if match_pattern in line:
                    seu_log_dict[info] = line.split(match_pattern)[1].strip()
                    unfound_info.remove(info)
                    found_info = True
                    break

            if not found_info:
                seu_log_dict[info] = np.nan

        return seu_log_dict, not ("register" in unfound_info), 0

    @classmethod
    def _read_golden_log(cls, run_info: RunInfo) -> pd.Series:
        """
        Read specifically the golden file.

        :param run_info: Configuration object
        :type run_info: RunInfo
        :raises ValueError: Raised if the golden log is unparsable for any reason. If
        this is the case one should make sure the configuration file patterns matches
        the log file.
        :return: Returns a series containing the information in the golden log specified
        by the configuration file.
        :rtype: pd.Series
        """
        log = dict()
        unfound_info = [info for info in run_info.comparison_data.entries]
        info_to_find = unfound_info.copy()
        path = os.path.join(run_info.data.directory, run_info.data.golden)
        with open(path, "r") as f:
            lines = f.readlines()

        for info in info_to_find:
            match_pattern = getattr(run_info.comparison_data, info)
            for line in lines:
                if match_pattern in line:
                    log[info] = line.split(match_pattern)[1].strip()
                    unfound_info.remove(info)
                    break

        if len(unfound_info) > 0:
            raise ValueError(f"Could not find {unfound_info} in golden log")

        return pd.Series(log)
