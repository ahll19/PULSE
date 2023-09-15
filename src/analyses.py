import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal.windows import gaussian

from .data_model import Node
from .colorprint import ColorPrinter
from .firmwares import SeuRunInfo, RunInfo

from typing import Tuple, Union


class CommonPlottingTools:
    pass


class Analyses:
    corruption_error_name = "Data Corruption Error"
    critical_error_name = "Critical Error"
    silent_error_name = "Silent Error"

    corruption_error_rate = "Data Corruption Error Rate"
    critical_error_rate = "Critical Error Rate"
    silent_error_rate = "Silent Error Rate"

    corruption_error_color = "orange"
    critical_error_color = "red"
    silent_error_color = "blue"

    @classmethod
    def binary_error_table_by_run_and_type(
        cls, node: Node, plot: bool = False
    ) -> pd.DataFrame:
        common_columns = node.seu_log.columns.intersection(node.golden_log.index)
        corruption_series = (
            (node.seu_log[common_columns] != node.golden_log).sum(axis=1).astype(bool)
        )
        critical_series = ~(node.masking_series.copy())
        corruption_series = corruption_series & ~critical_series
        silent_series = ~(corruption_series.astype(bool) | critical_series)

        result = pd.DataFrame(
            {
                cls.corruption_error_name: corruption_series,
                cls.critical_error_name: critical_series,
                cls.silent_error_name: silent_series,
            }
        ).astype(int)

        if plot:
            print("No visualization for binary error table.")

        return result

    @classmethod
    def error_rate_by_type(
        cls, node: Node, plot: bool = False
    ) -> Union[pd.Series, Tuple[pd.Series, plt.Figure]]:
        binary_error_table = cls.binary_error_table_by_run_and_type(node, plot=False)
        n = len(binary_error_table)
        result = binary_error_table.sum(axis=0) / n

        if not plot:
            return result

        fig, ax = plt.subplots()
        x = [cls.corruption_error_name, cls.critical_error_name, cls.silent_error_name]
        y = [
            result[cls.corruption_error_name],
            result[cls.critical_error_name],
            result[cls.silent_error_name],
        ]

        ax.bar(
            x,
            y,
            color=[
                cls.corruption_error_color,
                cls.critical_error_color,
                cls.silent_error_color,
            ],
        )

        ax.set_ylabel("Error rate")
        ax.set_title(f"Error rate on node {node.name}")

        return result, fig

    @classmethod
    def error_rate_by_type_in_children(
        cls, node: Node, plot: bool = False
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, plt.Figure]]:
        results = {
            child.name: cls.error_rate_by_type(child, plot=False)
            for child in node.children
        }
        result = pd.DataFrame(results).T

        # sort by silent error
        result = result.sort_values(cls.silent_error_name)

        if not plot:
            return result

        fig, ax = plt.subplots()

        result.plot.bar(
            ax=ax,
            stacked=True,
            color=[
                cls.corruption_error_color,
                cls.critical_error_color,
                cls.silent_error_color,
            ],
        )

        ax.set_xlabel("Children nodes")
        ax.set_ylabel("Error rate")
        ax.set_title(f"Error rate in children of node {node.name}")

        return result, fig

    @classmethod
    def error_rate_over_time(
        cls, node: Node, plot: bool = False
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, plt.Figure], None]:
        try:
            __test = SeuRunInfo.injection_cycle.name
        except AttributeError:
            print("No injection cycle info available. Cannot calculate error rate.")
            print("Perhaps change SeuRunInfo name in Analyses.error_rate_over_time()")
            return None

        binary_error_table = cls.binary_error_table_by_run_and_type(node, plot=False)
        injection_cycle_series = node.seu_log[
            SeuRunInfo.injection_cycle.name
        ].sort_values()
        binary_error_table = binary_error_table.loc[injection_cycle_series.index]
        binary_error_table.index = injection_cycle_series

        # Get the individual series
        corruption_series = binary_error_table[cls.corruption_error_name]
        critical_series = binary_error_table[cls.critical_error_name]
        silent_series = binary_error_table[cls.silent_error_name]

        # Moving average window
        n = len(injection_cycle_series)
        if n < 10e1:
            w_size = 1
        elif n < 10e2:
            w_size = 10
        else:
            w_size = int(n * 10e-2)

        # Calculate moving average
        corruption_series = corruption_series.rolling(w_size).mean()
        critical_series = critical_series.rolling(w_size).mean()
        silent_series = silent_series.rolling(w_size).mean()

        # forward and backfill NaNs
        corruption_series = corruption_series.fillna(method="ffill")
        critical_series = critical_series.fillna(method="ffill")
        silent_series = silent_series.fillna(method="ffill")
        corruption_series = corruption_series.fillna(method="bfill")
        critical_series = critical_series.fillna(method="bfill")
        silent_series = silent_series.fillna(method="bfill")

        # Set name of series
        corruption_series.name = cls.corruption_error_name
        critical_series.name = cls.critical_error_name
        silent_series.name = cls.silent_error_name

        result = pd.concat([corruption_series, critical_series, silent_series], axis=1)

        if not plot:
            return result

        fig, vis_err_ax = plt.subplots()
        sil_err_ax = vis_err_ax.twinx()

        corruption_series.plot(
            ax=vis_err_ax,
            label=cls.corruption_error_name,
            c=cls.corruption_error_color,
            ls="-",
        )
        critical_series.plot(
            ax=vis_err_ax,
            label=cls.critical_error_name,
            c=cls.critical_error_color,
            ls="-",
        )
        silent_series.plot(
            ax=sil_err_ax,
            label=cls.silent_error_name,
            c=cls.silent_error_color,
            ls="--",
        )

        vis_err_ax.set_xlabel("Injection cycle")
        vis_err_ax.set_title(f"Window size: {w_size}, #hits: {n}")

        vis_err_ax.set_ylabel("Corrupton and critical error rate")
        sil_err_ax.set_ylabel("Silent error rate")

        vis_err_ax.legend(loc="upper left")
        sil_err_ax.legend(loc="upper right")

        fig.suptitle(f"Error rate over time on node {node.name}")

        return result, fig
