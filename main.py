from src import ToolBox

import matplotlib as mpl

import os


def main():
    _ = ""

    data_path = os.path.join(os.getcwd(), "data")
    toolbox = ToolBox(data_path)
    toolbox.kendall_soft_error_correlation(visualize=True)
    toolbox.error_rate_summary(visualize=True)
    toolbox.hard_error_times_by_reg(visualize=True)
    toolbox.summary_statistics(visualize=True)

    _ = ""


if __name__ == "__main__":
    mpl.use("TkAgg")
    main()
