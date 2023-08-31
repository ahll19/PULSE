from src import DataReader
from src import InfoEnum

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import os


def main():
    data_path = os.path.join(os.getcwd(), "data")
    seu_data, golden_data = DataReader.get_data(data_path)


if __name__ == "__main__":
    mpl.use("TkAgg")

    main()
