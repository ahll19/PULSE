from typing import Tuple, Union

import matplotlib.pyplot as plt
import pandas as pd

from .base_tools import BaseTools, SeuLog
from .error_definitions import SilentError, DataCorruptionError, CriticalError


class IbexCoremarkTools(BaseTools):
    @classmethod
    def stacked_register_error_class(
        cls, seu_log: SeuLog, golden_log: pd.Series, visualize: bool = False
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, plt.figure]]:
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
