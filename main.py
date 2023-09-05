from src import ToolBox

import matplotlib as mpl

import os


def main():
    _ = ""

    data_path = os.path.join(os.getcwd(), "data")
    toolbox = ToolBox(data_path)
    toolbox.kendall_soft_error_correlation(visualize=False)
    toolbox.error_rate_summary(visualize=False)
    toolbox.hard_error_times_by_reg(visualize=False)
    toolbox.summary_statistics(visualize=False)
    toolbox.uniformity_test(visualize=True)

    _ = ""


if __name__ == "__main__":
    mpl.use("TkAgg")
    main()
