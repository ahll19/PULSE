from src import (
    DataInterface,
    RunInfo,
    BaseTools,
    SilentError,
    DataCorruptionError,
    CriticalError,
    IbexHwsecCoremarkTools,
)

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.special import comb
from anytree.exporter import DotExporter


if __name__ == "__main__":
    mpl.use("TkAgg")

    runinfo = RunInfo("src/run_info/ibex_hwsec_coremark.ini")
    data_interface = DataInterface(runinfo)
    all_data = data_interface.get_data_by_node(data_interface.root)

    name = "register_file_i"
    node = data_interface.get_node_by_name(name)[0]
    node_data = data_interface.get_data_by_node(node)

    root_data = data_interface.get_data_by_node(data_interface.root)

    alert_classifications = IbexHwsecCoremarkTools.alert_classification(
        root_data, data_interface.golden_log, True
    )

    _ = ""
