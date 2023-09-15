from src import RegisterTree, Analyses

import matplotlib as mpl
import matplotlib.pyplot as plt
from anytree.exporter import DotExporter

import os


def main():
    reg_tree = RegisterTree(
        data_directory=os.path.join(os.getcwd(), "data"), data_loading_timeout=120
    )

    rf_reg_name = "ibex_soc_wrap.ibex_soc_i.ibex_wrap.u_top.u_ibex_top.gen_regfile_ff.register_file_i"
    node = reg_tree.get_node_by_path(rf_reg_name)

    result, fig = Analyses.error_rate_by_type_in_children(node, plot=True)
    fig.show()

    DotExporter(reg_tree.root).to_picture("tree.png")
    _ = input("Keeping plot open. Press enter to stop script.")


if __name__ == "__main__":
    mpl.use("TkAgg")

    main()
