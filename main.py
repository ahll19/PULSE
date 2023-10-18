from src import (
    DataInterface,
    RunInfo,
    AnalysisTools,
    SilentError,
    DataCorruptionError,
    CriticalError,
)

import matplotlib as mpl
import matplotlib.pyplot as plt
from anytree.exporter import DotExporter


# TODO: Mode delimiter argument to config

if __name__ == "__main__":
    mpl.use("TkAgg")

    # Getting the data
    runinfo = RunInfo("src/run_info/ibex_coremark.ini")
    data_interface = DataInterface(runinfo)

    # Querying the data-interface
    path = "ibex_soc_wrap.ibex_soc_i.ibex_wrap.u_top.u_ibex_top.gen_regfile_ff.register_file_i"
    name = "ibex_wrap"

    node = data_interface.get_node_by_path(path)
    nodes = data_interface.get_node_by_name(name)

    node_data = data_interface.get_data_by_node(node)
    all_data = data_interface.get_data_by_node(data_interface.root)

    # Using the AnalysisTools
    node_errors, fig = AnalysisTools.error_classification(
        node_data, data_interface.golden_log, visualize=True
    )
    nodes_errors, fig = AnalysisTools.error_classification(
        all_data, data_interface.golden_log, visualize=True
    )

    _ = input("Press enter to continue...")
