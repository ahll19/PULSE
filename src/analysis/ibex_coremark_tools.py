from anytree import RenderTree, AsciiStyle, PreOrderIter 
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
        cls, data_interface: DataInterface, node: Node, visualize: bool = False, filter: bool = False
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

        :param filter: If True, remove zero register from plot
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
        plt_df.index = plt_df.index.map(regfile_name_map_ibex)
        if filter:
            # remove zero register from plot
            plt_df.drop("zero", inplace=True)
        plt_df.sort_values(by=CriticalError.name, inplace=True, ascending=False)

        fig, ax = plt.subplots()

        plt_df.plot.bar(
            stacked=True,
            ax=ax,
            color=[SilentError.color, DataCorruptionError.color, CriticalError.color]

        )

        ax.set_title(f"Error Classification: {node.name}")
        ax.set_ylabel("Proportion of errors")
        ax.set_xlabel("Register")

        plt.xticks(rotation=45)

        fig.show()

        return df, fig
    
    @classmethod
    def critical_signals(
        cls, data_interface: DataInterface, start_node: Node, n_signals: int = 20, visualize: bool = False, 
        clean_indexes: bool = True
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, plt.figure]]:
        """
        This method is used to find the most critical signals in the Coremark Ibex runs.
        It does this by finding each leaf node, i.e. the signals on which injections are done, 
        of the root node that was passed. Then the proportion of errors for each leaf node are calculated. 

        :param n_signals: The number of signals to return in the plot
        :param start_node: The node to start the search from
        :param visualize: If True, plot the results
        :return: A DataFrame of the most critical signals
        """

        # get all leaf nodes
        leaf_nodes = [node for node in PreOrderIter(start_node) if not node.children]

        # calculate error proportions
        node_err_props = BaseTools.register_error_props(data_interface, leaf_nodes) 
        
        if not visualize:
            return node_error_props
        
        fig, ax = plt.subplots()

        data_order = [CriticalError, DataCorruptionError, SilentError]
        plt_df = node_err_props.sort_values(by=CriticalError.name, ascending=False)
        plt_df = plt_df.head(n_signals)
        plt_df = plt_df[[error_class.name for error_class in data_order]]

        if clean_indexes:
            # filter out index names for a bunch of stuff
            plt_df.index = plt_df.index.map(lambda x: '.'.join(x.split('.')[6:]))
            plt_df.index = plt_df.index.str.replace('_i.', '.')
            plt_df.index = plt_df.index.str.replace('_q', '')
            plt_df.index = plt_df.index.str.replace('_o', '')
            plt_df.index = plt_df.index.str.replace('.gen_prefetch_buffer', '')

            def replace_substrings(label):
                for key in regfile_name_map_ibex:
                    if key in label:
                        label = label.replace(key, regfile_name_map_ibex[key])
                return label

            # Apply the custom function to filter each index label
            plt_df.index = plt_df.index.map(replace_substrings)

        plt_df.plot.barh(stacked=True, ax=ax, color=[error_class.color for error_class in data_order] )

        ax.invert_yaxis()
        ax.set_xlim(0, 1)
        ax.legend(loc='lower right', framealpha=1)
        
        ax.set_xlabel("Proportion of errors")
        fig.show()

        return node_err_props, fig

regfile_name_map_ibex = {
    "rf_reg[31]": "zero",
    "rf_reg[30]": "ra",
    "rf_reg[29]": "sp",
    "rf_reg[28]": "gp",
    "rf_reg[27]": "tp",
    "rf_reg[26]": "t0",
    "rf_reg[25]": "t1",
    "rf_reg[24]": "t2",
    "rf_reg[23]": "s0",
    "rf_reg[22]": "s1",
    "rf_reg[21]": "a0",
    "rf_reg[20]": "a1",
    "rf_reg[19]": "a2",
    "rf_reg[18]": "a3",
    "rf_reg[17]": "a4",
    "rf_reg[16]": "a5",
    "rf_reg[15]": "a6",
    "rf_reg[14]": "a7",
    "rf_reg[13]": "s2",
    "rf_reg[12]": "s3",
    "rf_reg[11]": "s4",
    "rf_reg[10]": "s5",
    "rf_reg[9]": "s6",
    "rf_reg[8]": "s7",
    "rf_reg[7]": "s8",
    "rf_reg[6]": "s9",
    "rf_reg[5]": "s10",
    "rf_reg[4]": "s11",
    "rf_reg[3]": "t3",
    "rf_reg[2]": "t4",
    "rf_reg[1]": "t5",
    "rf_reg[0]": "t6"
}

