from src import RegisterTree, Analyses, Config, DataStructure

import matplotlib as mpl
import matplotlib.pyplot as plt
from anytree.exporter import DotExporter

import os


def main1():
    config = Config("coremark")
    reg_tree = RegisterTree(config)

    rf_reg_name = "ibex_soc_wrap.ibex_soc_i.ibex_wrap.u_top.u_ibex_top.gen_regfile_ff.register_file_i"
    node = reg_tree.get_node_by_path(rf_reg_name)

    Analyses.binary_error_table_by_run_and_type(node, plot=True)
    Analyses.error_rate_by_type(node, plot=True)
    Analyses.error_rate_by_type_in_children(node, plot=True)
    Analyses.error_rate_over_time(node, plot=True)
    Analyses.test_coverage(node, plot=True)


def main2():
    config = Config("coremark")
    data_structure = DataStructure(config)


if __name__ == "__main__":
    mpl.use("TkAgg")

    main2()
