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

    ibex_coremark = RunInfo("src/run_info/ibex_coremark.ini")
    ic_interface = DataInterface(ibex_coremark)

    ibex_hwsec_coremark = RunInfo("src/run_info/ibex_hwsec_coremark.ini")
    ihc_interface = DataInterface(ibex_hwsec_coremark)

    name = "register_file_i"

    ic_node = ic_interface.get_node_by_name(name)[0]
    ic_node_data = ic_interface.get_data_by_node(ic_node)

    ihc_node = ihc_interface.get_node_by_name(name)[0]
    ihc_node_data = ihc_interface.get_data_by_node(ihc_node)

    ic_prob = IbexCoremarkTools.adjusted_probability(
        ic_node_data,
        ic_interface.golden_log,
        ibex_coremark.coverage.n_cycles,
        ibex_coremark.coverage.n_bits,
    )

    ihc_prob = IbexCoremarkTools.adjusted_probability(
        ihc_node_data,
        ihc_interface.golden_log,
        ibex_hwsec_coremark.coverage.n_cycles,
        ibex_hwsec_coremark.coverage.n_bits,
    )

    _ = input("Press enter to continue")
