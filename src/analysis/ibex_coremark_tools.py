from typing import Tuple, Union

import matplotlib.pyplot as plt
import pandas as pd

from .base_tools import BaseTools, SeuLog
from .structures import SilentError, DataCorruptionError, CriticalError


class IbexCoremarkTools(BaseTools):
    @classmethod
    def stacked_register_error_class(
        cls, seu_log: SeuLog, golden_log: pd.Series, visualize: bool = False
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, plt.figure]]:
        """
        This method is only supposed to be called on the rf_regfile_i node-data of the
        Coremark Ibex runs, but in theory it can be used on any node if you so wish.

        This method takes all unique register names in the SeuLog (all ancestor nodes)
        and computes the propoertion of errors on each one. Then it returns a dataframe
        with these error propoertions.

        The most usefel part of this method is visualizing and comparing the
        distribution of errors visualize for all unique ancestors of a node (in the
        intended case, each register of the core)

        :param seu_log: SeuLog of a given run. Can be queried from the DataInterface
        object, by usign a node.
        :type seu_log: SeuLog
        :param golden_log: Series showing the information parsed from the golden run.
        can be found on the golden_log attribute of the DataInterface class.
        :type golden_log: pd.Series
        :param visualize: Whether or not to visalize the results, defaults to False
        :type visualize: bool, optional
        :return: The dataframe with the error rates for each ancestor of the node-data.
        If visualize==True also returns the figure object from the visualization.
        :rtype: Union[pd.DataFrame, Tuple[pd.DataFrame, plt.figure]]
        """
        logs = {
            name: seu_log[seu_log["register"] == name]
            for name in seu_log["register"].unique()
        }
        for key in logs.keys():
            logs[key].name = key.split(".")[-1]

        error_classes = {
            name: cls.error_classification(log, golden_log, False)
            for name, log in logs.items()
        }

        value_counts = {
            name: error_class.value_counts()
            for name, error_class in error_classes.items()
        }

        proportions = {
            name: value_count / value_count.sum()
            for name, value_count in value_counts.items()
        }

        df = pd.DataFrame(proportions).fillna(0).T

        if not visualize:
            return df

        plt_df = df.copy()
        plt_df.index = plt_df.index.str.split(".").str[-1]
        plt_df.sort_values(by=CriticalError.name, inplace=True, ascending=False)

        fig, ax = plt.subplots()

        plt_df.plot.bar(
            stacked=True,
            ax=ax,
            color=[CriticalError.color, DataCorruptionError.color, SilentError.color],
        )

        ax.set_title(f"Error Classification: {seu_log.name}")
        ax.set_ylabel("Proportion of errors")
        ax.set_xlabel("Register")

        plt.xticks(rotation=45, ha="right")

        fig.show()

        return df, fig
