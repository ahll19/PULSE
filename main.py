from src.data_interface import DataInterface
from src.analysis.base_tools import BaseTools
from src.analysis.ibex_coremark_tools import IbexCoremarkTools
from src.analysis.ibex_hwsec_coremark_tools import IbexHwsecCoremarkTools
from src.run_info.run_info import RunInfo

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.special import comb
from anytree.exporter import DotExporter


def visualization_setup():
    # Interactive plots. Requires tkinter on the machine running the code
    mpl.use("TkAgg")
    # Latex formatting for plots. Some visualizations might not work without this
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["mathtext.fontset"] = "dejavuserif"


if __name__ == "__main__":
    visualization_setup()

    runinfo = RunInfo("src/run_info/ibex_hwsec_coremark.ini")
    data_interface = DataInterface(runinfo)

    golden = data_interface.golden_log
    node = data_interface.get_node_by_name("register_file_i")[0]
    root = data_interface.root
    node_data = data_interface.get_seu_log_by_node(node)
    root_data = data_interface.get_seu_log_by_node(root)

    node_runs = list(node_data.index)
    # opt_node = data_interface.optional_data.get_data_by_runs(node_runs)

    # _ = BaseTools.error_classification(data_interface, root, visualize=True)

    # _ = BaseTools.windowed_error_rate(
    #     data_interface, node, "injection_cycle", visualize=True, window_size=100
    # )
    # _ = BaseTools.error_classification_confidence(data_interface, node, visualize=True)
    # _ = BaseTools.expected_num_multi_injection_runs(
    #     500_000, 2200, [100, 100_000], visualize=True
    # )

    # _ = IbexCoremarkTools.stacked_register_error_class(
    #     data_interface, node, visualize=True
    # )

    # _ = IbexHwsecCoremarkTools.alert_classification_and_error_counts(
    #     data_interface, node, visualize=True
    # )

    _ = input()
