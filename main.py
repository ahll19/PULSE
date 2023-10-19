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
from anytree.exporter import DotExporter


if __name__ == "__main__":
    mpl.use("TkAgg")

    runinfo = RunInfo("src/run_info/ibex_coremark.ini")
    data_interface = DataInterface(runinfo)
    all_data = data_interface.get_data_by_node(data_interface.root)

    name = "register_file_i"
    node = data_interface.get_node_by_name(name)[0]
    node_data = data_interface.get_data_by_node(node)

    IbexCoremarkTools.stacked_register_error_class(
        node_data, data_interface.golden_log, visualize=True
    )

    _ = input("Press enter to continue")
