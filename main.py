from src import DataReader, ToolBox

import matplotlib as mpl

import os


def main():
    _ = ""

    data_path = os.path.join(os.getcwd(), "data")
    toolbox = ToolBox(data_path)
    toolbox.kendall_soft_error_correlation(visualize=False)
    toolbox.error_rate_summary(visualize=True)


if __name__ == "__main__":
    mpl.use("TkAgg")
    main()
