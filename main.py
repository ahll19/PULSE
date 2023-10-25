from src import (
    DataInterface,
    RunInfo,
    BaseTools,
    SilentError,
    DataCorruptionError,
    CriticalError,
    IbexCoremarkTools,
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

    ibex_coremark = RunInfo("src/run_info/ibex_coremark.ini")
    ic_interface = DataInterface(ibex_coremark)

    name = "register_file_i"

    ic_node = ic_interface.get_node_by_name(name)[0]
    ic_node_data = ic_interface.get_data_by_node(ic_node)
    all_data = ic_interface.get_data_by_node(ic_interface.root)

    IbexCoremarkTools.variance_num_multi_injection_runs(
        n_runs=32_000, n_target_bits=5600, n_injection_cycles=40_000
    )

    _ = ""
