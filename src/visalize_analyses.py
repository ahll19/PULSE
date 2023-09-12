from .analyses import Analyses
from .register_tree import RegisterTree
from .data_reader import DataReader
from .enums import RunInfoEnum
from .register_tree import Node

from typing import List, Tuple

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class PlotHelper:
    pass


class Visualizer:
    @classmethod
    def error_rates_in_worst_nodes(
        cls,
        register_tree: RegisterTree = None,
        nodes: List[Node] = None,
        n_nodes: int = 20,
        max_levels_in_path: int = 0,
    ) -> plt.figure:
        if register_tree is None and nodes is None:
            print("Please provide either a register tree or a list of nodes")
            return None

        if register_tree is not None and nodes is not None:
            print("Please provide either a register tree or a list of nodes, not both")
            return None

        if register_tree is not None:
            _result = register_tree.run_analysis_on_all_nodes(func=Analyses.error_rate)
            result = list()

            for node, error_rate in _result:
                if error_rate is None:
                    continue

                if max_levels_in_path <= 0:
                    res = (node.soc_path, error_rate)
                else:
                    split_path = node.soc_path.split(".")
                    if max_levels_in_path > len(split_path):
                        res = (node.soc_path, error_rate)
                    else:
                        res = (
                            ".".join(split_path[-max_levels_in_path:]),
                            error_rate,
                        )

                result.append(res)
            result.sort(key=lambda x: x[1], reverse=True)
            result = result[:n_nodes]
        else:
            result = list()
            for node in nodes:
                error_rate = Analyses.error_rate(node)
                if error_rate is None:
                    continue

                if max_levels_in_path <= 0:
                    res = (node.soc_path, error_rate)
                else:
                    split_path = node.soc_path.split(".")
                    if max_levels_in_path > len(split_path):
                        res = (node.soc_path, error_rate)
                    else:
                        res = (
                            ".".join(split_path[-max_levels_in_path:]),
                            error_rate,
                        )
                result.append(res)
            result.sort(key=lambda x: x[1], reverse=True)
            result = result[:n_nodes]

        fig, ax = plt.subplots()
        ax.bar([x[0] for x in result], [x[1] for x in result])
        ax.set_xticklabels([x[0] for x in result], rotation=90)
        ax.set_ylabel("Error Rate")
        ax.set_title("Error Rates in Worst Nodes")

        fig.show()

        return fig

    @classmethod
    def error_type_distribution(cls, data_reader: DataReader) -> plt.figure:
        big_binary_table = Analyses.binary_error_table_by_type(
            data_reader.seu_log_frame,
            data_reader.masking_series,
            data_reader.golden_log,
        )
        n_entries = len(big_binary_table)

        parsable_error_columns = big_binary_table.columns.intersection(
            data_reader.get_golden_log().index
        )

        n_error_entries = len(
            big_binary_table[big_binary_table[parsable_error_columns].sum(axis=1) > 0]
        )
        n_silent_entries = n_entries - n_error_entries

        sum_series = big_binary_table.sum(axis=0)
        sum_series["Silent"] = n_silent_entries
        rate_series = sum_series * 100 / n_entries

        fig, ax = plt.subplots()

        rate_series.plot.bar(ax=ax, logy=True)
        ax.set_ylabel("Error Rate")
        ax.set_title(f"Percent of Runs With Error Type (#Runs: {n_entries})")

        for p in ax.patches:
            val = (p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.01)
            p_val = f"{val[0]:.1f}"
            ax.annotate(p_val, xy=val[1], color="blue")

        fig.show()

        return fig

    @classmethod
    def error_type_macro_distribution(cls, data_reader: DataReader) -> plt.figure:
        big_binary_table = Analyses.binary_error_table_by_type(
            data_reader.seu_log_frame,
            data_reader.masking_series,
            data_reader.golden_log,
        )

        parsable_error_columns = big_binary_table.columns.intersection(
            data_reader.get_golden_log().index
        )
        n_entries = len(big_binary_table)
        n_error_entries = len(
            big_binary_table[big_binary_table[parsable_error_columns].sum(axis=1) > 0]
        )
        n_silent_entries = n_entries - n_error_entries
        n_unparsable_entries = big_binary_table[Analyses.failed_to_parse_column].sum()

        s_err = n_silent_entries * 100 / n_entries
        par_err = n_error_entries * 100 / n_entries
        unpar_err = n_unparsable_entries * 100 / n_entries

        fig, ax = plt.subplots()

        ax.bar(
            ["Silent", "Parsed", "Failed to Parse"],
            [s_err, par_err, unpar_err],
        )
        ax.set_yscale("log")
        ax.set_ylabel("Error Rate")
        ax.set_title(f"Percent of Runs With Macro Error Type (#Runs: {n_entries})")

        for p in ax.patches:
            val = (p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.01)
            p_val = f"{val[0]:.3f}"
            ax.annotate(p_val, xy=val[1], color="blue")

        fig.show()

        return fig

    @classmethod
    def error_rate_over_time(
        cls, data_reader: DataReader, window_size: int = 10000
    ) -> plt.figure:
        error_table = Analyses.error_rate_over_time(
            data_reader.seu_log_frame,
            data_reader.masking_series,
            data_reader.golden_log,
            window_size,
        )

        silent = Analyses.silent_column
        parsed = Analyses.parsed_column
        failed = Analyses.failed_to_parse_column
        time = RunInfoEnum.injection_cycle.name

        fig, ax = plt.subplots()
        silent_ax = ax.twinx()

        ax.plot(
            error_table[time],
            error_table[parsed],
            label="Parsed",
            alpha=0.5,
            color="green",
            ls="",
            marker=".",
        )
        ax.plot(
            error_table[time],
            error_table[failed],
            label="Failed to Parse",
            alpha=0.5,
            color="red",
            ls="",
            marker=".",
        )
        silent_ax.plot(
            error_table[time],
            error_table[silent],
            label="Silent",
            alpha=0.5,
            color="blue",
            ls="",
            marker=".",
        )

        def ns_to_largest_format(ns: int) -> Tuple[float, str]:
            if ns < 10e3:
                return ns, "ns"
            elif ns < 10e6:
                return ns / 10e3, r"$\mu$-seconds"
            elif ns < 10e9:
                return ns / 10e6, "ms"
            elif ns < 10e12:
                return ns / 10e9, "s"

        time, time_format = ns_to_largest_format(window_size)

        ax.set_ylabel("Error Rate (Parsed and Failed to Parse)")
        silent_ax.set_ylabel("Error Rate (Silent)")
        ax.set_xlabel("Time")
        ax.set_title(f"Window size: {time:.2f} {time_format}")
        ax.legend(loc="lower left")
        silent_ax.legend(loc="lower right")

        fig.show()

        return fig
