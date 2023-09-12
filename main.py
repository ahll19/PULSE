from src import DataReader, Analyses, Visualizer, ColorPrinter, RegisterTree

import matplotlib as mpl

import os


def test_all_analyses(data_reader: DataReader, reg_tree: RegisterTree):
    ColorPrinter.print_okcyan("Running all analyses on all nodes")
    # get list of methods from Analyses class
    analyses_methods = [
        method
        for method in dir(Analyses)
        if callable(getattr(Analyses, method)) and not method.startswith("__")
    ]

    for method in analyses_methods:
        ColorPrinter.print_bold(f"Running {method}")
        try:
            reg_tree.run_analysis_on_all_nodes(
                func=getattr(Analyses, method),
            )
        except Exception as e:
            ColorPrinter.print_fail(f"Failed {method}")
            ColorPrinter.print_fail(e)

            continue

        ColorPrinter.print_okgreen(f"Finished Analysis: {method}")


def main(test_analyses: bool = True):
    data_path = os.path.join(os.getcwd(), "data")
    data_reader = DataReader(data_path, timeout_time=120)
    reg_tree = RegisterTree(os.path.join(data_path, "reg_tree.txt"), data_reader)

    if test_analyses:
        test_all_analyses(data_reader, reg_tree)

    Visualizer.error_rates_in_worst_nodes(reg_tree)


if __name__ == "__main__":
    mpl.use("TkAgg")
    main(test_analyses=True)
