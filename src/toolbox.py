import os
from typing import List, Tuple
from itertools import combinations
import sys

import pandas as pd
import numpy as np
from scipy.stats import kendalltau
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

from .colorprint import ColorPrinter
from .data_reader import DataReader
from .enums import SoftErrorIndicatorEnum, SeuDescriptionEnum


class ToolBox:
    data_dir_path: str = None

    golden_num: pd.Series = None
    # golden_instr: pd.DataFrame = None
    seu_soft_num: pd.DataFrame = None
    seu_hard_num: pd.Series = None
    golden_num: pd.Series = None

    _valid_file_names: List[str] = ["golden.log", "golden.txt", "diff.log", "log.txt"]

    def __init__(self, data_dir_path: str) -> None:
        self.data_dir_path = data_dir_path

        self.__check_data_dir()
        self.__set_logs()
        self.__set_seu_num()

    def register_error_rates(self, visualize: bool = False) -> pd.DataFrame:
        soft_copy = self.seu_soft_num.copy()
        hard_copy = self.seu_hard_num.copy()
        reg_copy = self.seu_log.copy()[SeuDescriptionEnum.register.name]
        error_frame = pd.concat([soft_copy, hard_copy, reg_copy], axis=1)

        error_names = [enum.name for enum in SoftErrorIndicatorEnum] + ["hard error"]

        # Only look at rows with errors
        error_frame = error_frame[
            (error_frame.T.drop(SeuDescriptionEnum.register.name) != 0).any()
        ]

        # Get number of reg hits before removing non error entries
        reg_hit_count = reg_copy.value_counts()

        # remove rows from reg_copy where error frame idx is not in reg_copy
        reg_copy = reg_copy[reg_copy.index.isin(error_frame.index)]

        # Add number of error occurrences by register
        error_frame = error_frame.groupby(SeuDescriptionEnum.register.name).sum()

        # Remove entries from reg_hit_count where the register is not in error_frame
        reg_hit_count = reg_hit_count[reg_hit_count.index.isin(error_frame.index)]

        # Divide rows of error_frame by reg_hit_count (by common index)
        for register in reg_hit_count.index:
            error_frame.loc[register] = (
                error_frame.loc[register] / reg_hit_count.loc[register]
            )

        if not visualize:
            return error_frame

        fig, ax_rate = plt.subplots()

        # Map registers to indices and the other way around
        reg_idx_map = {register: i for i, register in enumerate(error_frame.index)}
        idx_reg_map = {i: register for i, register in enumerate(error_frame.index)}

        # Add reg_hit_count, from top down
        ax_count = ax_rate.twinx()
        reg_hit_count.plot.bar(ax=ax_count, logy=True, color="black", alpha=0.25)

        # Labels
        ax_rate.set_xlabel("Register")
        ax_rate.set_ylabel("Error Rate (Colored Bars)")
        ax_count.set_ylabel("Register Hits, (Gray Bars)")

        # change yticks from science to decimal
        ax_rate.yaxis.set_major_formatter(ScalarFormatter())
        ax_count.yaxis.set_major_formatter(ScalarFormatter())

        # change xticks to idx
        error_frame.plot.bar(ax=ax_rate, logy=True)
        tick_locs = ax_rate.xaxis.get_ticklocs().astype(int)
        tick_names = [idx_reg_map[i] for i in tick_locs]
        new_tick_values = [reg_idx_map[register] for register in tick_names]
        ax_rate.xaxis.set_ticks(tick_locs)
        ax_rate.xaxis.set_ticklabels(new_tick_values)

        # add grids
        ax_rate.grid(axis="y", which="major", ls="-", alpha=0.5)
        ax_count.grid(axis="y", which="major", ls="--")

        ColorPrinter.print_bold_okcyan("Registers are mapped on the plot as follows:")
        for i, register in idx_reg_map.items():
            ColorPrinter.print_okcyan(f"{i} -> {register}")

    def kendall_soft_error_correlation(
        self, significant_level: float = 0.05, visualize: bool = False
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Calculates the Kendall's tau correlation matrix and the matrix of significant
        p-values for the soft error indicators. We condition the data on when we have
        a soft error. Otherwise we skew the results since most runs don't cauase soft
        errors.

        This test is designed to see how often soft errors occur together.

        Args:
            significant_level (float, optional): The significance level. Defaults to 5%.
            visualize (bool, optional): Visualize the results? Defaults to False.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing the Kendall's tau
            correlation matrix and the matrix of significant p-values.
        """
        # get rows where at least one soft error occurred
        soft_non_zero = self.seu_soft_num.copy()
        soft_non_zero = soft_non_zero[(soft_non_zero.T != 0).any()]

        soft_names = [enum.name for enum in SoftErrorIndicatorEnum]
        p_matrix = pd.DataFrame(index=soft_names, columns=soft_names, dtype=float)

        correlation_matrix = soft_non_zero.corr(method="kendall")

        for i, j in combinations(SoftErrorIndicatorEnum, 2):
            _, p_value = kendalltau(soft_non_zero[i.name], soft_non_zero[j.name])
            p_matrix[i.name][j.name] = p_value
            p_matrix[j.name][i.name] = p_value

        p_matrix = p_matrix.fillna(0)
        significant_matrix = p_matrix < significant_level

        if not visualize:
            return correlation_matrix, significant_matrix

        fig, [ax_all, ax_sig] = plt.subplots(nrows=2, sharex=True, sharey=True)
        np_sig = np.array(significant_matrix)
        np_corr = np.array(correlation_matrix)
        np_sig_corr = np_corr.copy()
        x, y = np_sig.shape
        all_black = np.ones((x, y, 4))
        for i in range(np_sig.shape[0]):
            for j in range(np_sig.shape[1]):
                if np_sig[i, j] and i != j:
                    all_black[i, j] = np.array([1, 1, 1, 0])
                else:
                    all_black[i, j] = np.array([0, 0, 0, 255])

        np_sig_corr[np_sig == False] = 0

        np.fill_diagonal(np_sig_corr, 0)
        vmin, vmax = -1, 1

        cb_all = ax_all.imshow(
            np_corr, cmap="bwr", interpolation="none", vmin=vmin, vmax=vmax
        )
        cb_sig = ax_sig.imshow(
            np_sig_corr, cmap="bwr", interpolation="none", vmin=vmin, vmax=vmax
        )
        ax_sig.imshow(all_black, interpolation="none")

        fig.colorbar(cb_all, ax=ax_all, shrink=0.8)
        fig.colorbar(cb_sig, ax=ax_sig, shrink=0.8)

        ax_all.set_xticks(range(len(soft_names)))
        ax_all.set_yticks(range(len(soft_names)))
        ax_all.set_xticklabels(soft_names)
        ax_all.set_yticklabels(soft_names)

        plt.setp(ax_all.get_xticklabels(), rotation=45)

        fig.suptitle("Kendall's Tau Correlation Matrix")
        ax_all.set_title("All correlation values")
        ax_sig.set_title("Significant correlation values")

        for ax in [ax_all, ax_sig]:
            plt.sca(ax)
            plt.xticks(rotation=45)

        plt.show()

        return correlation_matrix, significant_matrix

    @ColorPrinter.print_func_time
    def __check_data_dir(self) -> None:
        if not os.path.isdir(self.data_dir_path):
            ColorPrinter.print_bold_fail(f"Data directory path does not exist:")
            raise ValueError(self.data_dir_path)

        for path, _, files in os.walk(self.data_dir_path):
            for name in files:
                if name not in self._valid_file_names:
                    ColorPrinter.print_warning(
                        f"Unexpected file in data directory: {name} in {path}"
                    )

    @ColorPrinter.print_func_time
    def __set_logs(self) -> None:
        self.seu_log, self.golden_num = DataReader.get_data(self.data_dir_path)

    @ColorPrinter.print_func_time
    def __set_seu_num(self) -> None:
        if self.seu_log is None:
            ColorPrinter.print_bold_fail("SEU log not set")
            raise ValueError("SEU log not set")

        # This depends on soft error data being saved in the golden log as well
        # We find all entries in the soft log which are different from the golden log
        soft_error_names = [enum.name for enum in SoftErrorIndicatorEnum]
        soft = self.seu_log.copy()[soft_error_names]
        soft = soft - self.golden_num
        soft = (soft != 0).astype(int)
        self.seu_soft_num = soft

        # This is just a simple conversion for now since we save a binary value for
        # the hard error runs
        hard = self.seu_log.copy()["hard error"].astype(int)
        self.seu_hard_num = hard
