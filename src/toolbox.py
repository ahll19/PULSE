import os
from typing import Dict, List, Tuple
from itertools import combinations

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kendalltau
from sklearn.neighbors import KernelDensity

from .colorprint import ColorPrinter
from .data_reader import DataReader
from .enums import SoftErrorIndicatorEnum, SeuDescriptionEnum


class ToolBox:
    data_dir_path: str = None
    max_ram_usage: float = None
    max_time: float = None

    seu_log: pd.DataFrame = None
    seu_soft_num: pd.DataFrame = None
    seu_hard_num: pd.Series = None
    golden_num: pd.Series = None

    _valid_file_names: List[str] = ["golden.log", "golden.txt", "diff.log", "log.txt"]

    def __init__(
        self, data_dir_path: str, max_ram_usage: float = 8.0, max_time: float = 180.0
    ) -> None:
        self.data_dir_path = data_dir_path
        self.max_ram_usage = max_ram_usage
        self.max_time = max_time

        self.__check_data_dir()
        self.__set_logs()
        self.__set_seu_num()

    @ColorPrinter.print_func_time
    def uniformity_test(self, visualize: bool = False) -> None:
        """
        Shows a histogram of the injection clock cycle for each run. This is a
        visualization of the uniformity of the injection clock cycle.

        Args:
            visualize (bool, optional): Be true if u want plots. Defaults to False.
        """
        if not visualize:
            return

        err_binary_cycle = (
            self.seu_soft_num.copy().apply(lambda row: row.any(), axis=1).astype(int)
        ).rename("soft error")
        err_binary_cycle = pd.concat(
            [
                err_binary_cycle,
                self.seu_log[SeuDescriptionEnum.injection_clock_cycle.name],
            ],
            axis=1,
        )
        err_binary_cycle["error"] = err_binary_cycle["soft error"] | self.seu_hard_num
        err_binary_cycle.drop("soft error", axis=1, inplace=True)

        error_times = err_binary_cycle[err_binary_cycle["error"] == 1][
            SeuDescriptionEnum.injection_clock_cycle.name
        ].values

        fig, ax = plt.subplots()
        n_bins = 100

        ax.hist(
            error_times,
            bins=n_bins,
            histtype="step",
            alpha=0.5,
        )

        ax.set_title("Binned Error Times")
        ax.set_xlabel("Injection clock cycle")
        ax.set_ylabel("Density")
        fig.show()

    @ColorPrinter.print_func_time
    def summary_statistics(self, visualize: bool = False) -> None:
        """
        Just some basic summary statistics for the data.

        Args:
            visualize (bool, optional): viz or no viz. Defaults to False.
        """
        if not visualize:
            return

        # ==============================================================================
        # Getting broad distribution of error types
        # ==============================================================================
        err_catagory = pd.DataFrame(
            index=self.seu_log.index.copy(),
            data={
                "soft": self.seu_soft_num.apply(lambda x: x.any(), axis=1),
                "hard": self.seu_hard_num,
            },
        )
        err_catagory["invisisble"] = err_catagory.apply(
            lambda x: not (x["soft"] or x["hard"]), axis=1
        )

        err_catagory = err_catagory.astype(bool)
        err_catagory["only soft"] = err_catagory["soft"] & ~err_catagory["hard"]
        err_catagory["only hard"] = err_catagory["hard"] & ~err_catagory["soft"]
        err_catagory["hard & soft"] = err_catagory["hard"] & err_catagory["soft"]
        err_catagory.drop(["soft", "hard"], axis=1, inplace=True)
        err_catagory = err_catagory.astype(int)

        total = err_catagory.sum()
        fig, ax = plt.subplots()
        ax.set_title("Distribution of error types")
        total.plot.bar(ax=ax, color="tab:blue", alpha=0.5, logy=True)
        ax.set_ylabel("Number of runs")
        ax.set_xlabel("Error type")
        ax.set_xticklabels(total.index, rotation=45)
        for i, v in enumerate(total):
            ax.text(
                i,
                v,
                str(v) + " (" + str(round(v / total.sum() * 100, 2)) + "%)",
                color="tab:blue",
                fontweight="bold",
                ha="center",
                va="bottom",
            )

        fig.tight_layout()
        fig.show()
        # ==============================================================================

        # ==============================================================================
        # Smoothed error rate by catgeory
        # ==============================================================================
        tw_smooth_percent = 10e-3
        err_rate_category = err_catagory.copy()
        clock_cycle_series = self.seu_log[SeuDescriptionEnum.injection_clock_cycle.name]
        log_time_window = clock_cycle_series.max() - clock_cycle_series.min()
        smooth_window_len = int(log_time_window * tw_smooth_percent)

        for col in err_rate_category.columns:
            err_rate_category[col] = (
                err_rate_category[col]
                .rolling(window=smooth_window_len, center=True, win_type="blackman")
                .mean()
            )
        _plotting_frame = err_rate_category.copy()
        _plotting_frame["cycle"] = clock_cycle_series.values
        fig, err_ax = plt.subplots()
        invis_ax = err_ax.twinx()

        err_ax.set_title("Error rate by category")
        err_ax.set_xlabel("Injection clock cycle")
        err_ax.set_ylabel("Error rate")
        invis_ax.set_ylabel("Error rate")

        _plotting_frame.plot(
            x="cycle",
            y=["only soft", "only hard", "hard & soft"],
            ax=err_ax,
            color=["tab:blue", "tab:orange", "tab:green"],
            alpha=0.5,
        )
        _plotting_frame.plot(
            x="cycle",
            y="invisisble",
            ax=invis_ax,
            color="k",
            alpha=0.5,
            ls="--",
        )

        fig.tight_layout()
        fig.show()
        # ==============================================================================

    @ColorPrinter.print_func_time
    def hard_error_times_by_reg(
        self, visualize: bool = False, max_num_plots: int = 10
    ) -> Dict["str", pd.DataFrame]:
        # TODO: Extend to multicolor scatter plot by error types
        """
        Returns a dictionary containing the hard error times for each register.

        Returns:
            Dict["str", pd.DataFrame]: A dictionary containing the hard error times for
            each register.
        """
        hard_error_with_time = self.seu_log.copy()[
            [
                "hard error",
                SeuDescriptionEnum.injection_clock_cycle.name,
                SeuDescriptionEnum.register.name,
            ]
        ]

        hewt_dict_by_reg = dict()
        for register in hard_error_with_time[SeuDescriptionEnum.register.name].unique():
            if (
                hard_error_with_time[
                    hard_error_with_time[SeuDescriptionEnum.register.name] == register
                ]["hard error"].sum()
                == 0
            ):
                continue

            tmp = hard_error_with_time[
                hard_error_with_time[SeuDescriptionEnum.register.name] == register
            ]
            hewt_dict_by_reg[register] = tmp[
                [
                    "hard error",
                    SeuDescriptionEnum.injection_clock_cycle.name,
                ]
            ].astype(int)

        if not visualize:
            return hewt_dict_by_reg

        for i, (reg, table) in enumerate(hewt_dict_by_reg.items()):
            if i >= max_num_plots:
                break
            fig, ax = plt.subplots()
            ax.set_title(f"Reg: {reg}")
            ax.set_xlabel("Injection clock cycle")
            ax.set_ylabel("Error binary")

            table.plot.scatter(
                x=SeuDescriptionEnum.injection_clock_cycle.name,
                y="hard error",
                ax=ax,
                marker="x",
                s=10,
                alpha=1,
            )
            ax.set_yticks([0, 1])
            ax.set_yticklabels(["No error", "Error"])

            fig.tight_layout()
            fig.show()

        return hewt_dict_by_reg

    @ColorPrinter.print_func_time
    def error_rate_summary(self, visualize: bool = False) -> pd.DataFrame:
        """
        Calculates the error rate for each register. The error rate is defined as the
        number of times an error occured in a register divided by the number of times
        the register was hit.

        Args:
            visualize (bool, optional): To plot or not to plot. Defaults to False.

        Returns:
            pd.DataFrame: A dataframe containing the error rate for each register.
        """
        _ = ""
        soft_copy = self.seu_soft_num.copy()
        hard_copy = self.seu_hard_num.copy()

        # any errors occured series
        soft_copy = soft_copy.any(axis=1).astype(int)
        error_occured_series = (hard_copy + soft_copy).astype(bool).astype(int)

        # get register series
        reg_copy = self.seu_log.copy()[SeuDescriptionEnum.register.name]

        # combine regs and error series to dataframe
        error_frame = pd.concat([reg_copy, error_occured_series], axis=1)
        error_frame.columns = ["register", "error"]

        # get the number of hits in each registry
        reg_hit_count = reg_copy.value_counts()

        # get error count by register
        error_frame = error_frame.groupby("register").sum()

        # get error rate
        err_rate_dict = dict()
        for register in reg_hit_count.index:
            err_rate_dict[register] = (
                error_frame.loc[register] / reg_hit_count.loc[register]
            )
        error_reg_frame = pd.DataFrame(err_rate_dict).T
        error_reg_frame.columns = ["error rate"]

        # insert error count by register into error_reg_frame
        error_reg_frame.insert(0, "n hits", reg_hit_count)

        # sort
        error_reg_frame = error_reg_frame.sort_values(by="error rate", ascending=False)

        if not visualize:
            return error_reg_frame

        # remove rows with no hits
        plotting_err_reg_frame = error_reg_frame.copy()
        plotting_err_reg_frame = plotting_err_reg_frame[
            plotting_err_reg_frame["error rate"] != 0
        ]

        fig, rate_ax = plt.subplots()
        count_ax = rate_ax.twinx()

        rate_ax.set_ylabel("Error rate")
        count_ax.set_ylabel("Number of hits")
        rate_ax.set_xlabel("Register")
        rate_ax.set_title("Error rate by register")

        rate_ax.set_yscale("log")
        count_ax.set_yscale("log")

        rate_ax.bar(
            list(range(len(plotting_err_reg_frame.index))),
            plotting_err_reg_frame["error rate"],
            color="tab:red",
            alpha=0.5,
        )
        count_ax.bar(
            list(range(len(plotting_err_reg_frame.index))),
            plotting_err_reg_frame["n hits"],
            color="tab:blue",
            alpha=0.5,
        )

        rate_ax.tick_params(axis="y", labelcolor="tab:red")
        count_ax.tick_params(axis="y", labelcolor="tab:blue")

        rate_ax.grid()
        count_ax.grid(axis="y", ls="--")

        fig.tight_layout()
        fig.show()

        return error_reg_frame

    @ColorPrinter.print_func_time
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
        self.seu_log, self.golden_num = DataReader.get_data(
            self.data_dir_path,
            self.max_ram_usage,
            self.max_time,
        )

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
