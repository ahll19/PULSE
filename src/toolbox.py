import os
from typing import List, Tuple
from itertools import combinations

import pandas as pd
import numpy as np
from scipy.stats import kendalltau
import matplotlib.pyplot as plt

from .colorprint import ColorPrinter
from .data_reader import DataReader
from .enums import SoftErrorIndicatorEnum


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
        np_sig_corr[np_sig == False] = 0
        np.fill_diagonal(np_sig_corr, 0)
        vmin, vmax = -1, 1

        cb_all = ax_all.imshow(
            np_corr, cmap="bwr", interpolation="none", vmin=vmin, vmax=vmax
        )
        cb_sig = ax_sig.imshow(
            np_sig_corr, cmap="bwr", interpolation="none", vmin=vmin, vmax=vmax
        )

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
