from src import DataReader
from src import InfoEnum

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import os


def plot_register_distribution(data: pd.DataFrame) -> None:
    fig, ax = plt.subplots()
    counts = data["register"].value_counts()
    names = counts.index
    values = counts.values
    counter = list(range(len(names)))

    ax.bar(counter, values)
    fig.show()


def main():
    data_path = os.path.join(os.getcwd(), "data")
    seu_data, golden_data = DataReader.get_data(data_path)

    plot_register_distribution(seu_data)


if __name__ == "__main__":
    mpl.use("TkAgg")

    main()
