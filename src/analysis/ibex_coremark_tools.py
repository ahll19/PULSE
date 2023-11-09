from typing import Tuple, Union, Dict

import matplotlib.pyplot as plt
import pandas as pd

from .base_tools import BaseTools
from ..data_interface import DataInterface, Node
from .structures.error_definitions import (
    SilentError,
    DataCorruptionError,
    CriticalError,
)


class IbexCoremarkTools(BaseTools):
    @classmethod
    def stacked_register_error_class(
        cls, data_interface: DataInterface, node: Node, visualize: bool = False
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
        """
        children: Dict[str, Node] = {child.name: child for child in node.children}

        error_classes = {
            name: cls.error_classification(data_interface, child_node, False)
            for name, child_node in children.items()
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

        ax.set_title(f"Error Classification: {node.name}")
        ax.set_ylabel("Proportion of errors")
        ax.set_xlabel("Register")

        plt.xticks(rotation=45, ha="right")

        fig.show()

        return df, fig
