from src import (
    DataInterface,
    RunInfo,
    BaseTools,
    SilentError,
    DataCorruptionError,
    CriticalError,
)

import matplotlib as mpl
import matplotlib.pyplot as plt
from anytree.exporter import DotExporter


# TODO: Check that parsin is done correctly, and change the ini to match the log better
# TODO: Extend coremark analysis to include the stacked by register plot

if __name__ == "__main__":
    mpl.use("TkAgg")

    runinfo = RunInfo("src/run_info/ibex_coremark.ini")
    data_interface = DataInterface(runinfo)
    all_data = data_interface.get_data_by_node(data_interface.root)

    name = "register_file_i"
    node = data_interface.get_node_by_name(name)[0]
    node_data = data_interface.get_data_by_node(node)

    BaseTools.windowed_error_rate(
        node_data,
        data_interface.golden_log,
        "injection_cycle",
        visualize=True,
    )

    BaseTools.windowed_error_rate(
        all_data,
        data_interface.golden_log,
        "injection_cycle",
        visualize=True,
    )

    _ = input("Press enter to continue...")

    runinfo = RunInfo("src/run_info/ibex_hwsec_coremark.ini")
    data_interface = DataInterface(runinfo)
    all_data = data_interface.get_data_by_node(data_interface.root)

    name = "register_file_i"
    node = data_interface.get_node_by_name(name)[0]
    node_data = data_interface.get_data_by_node(node)

    BaseTools.windowed_error_rate(
        node_data,
        data_interface.golden_log,
        "injection_cycle",
        visualize=True,
    )

    BaseTools.windowed_error_rate(
        all_data,
        data_interface.golden_log,
        "injection_cycle",
        visualize=True,
    )

    _ = input("Press enter to continue...")
