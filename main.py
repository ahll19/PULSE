import os
from src import DataReader


def main():
    data_path = os.path.join(os.getcwd(), "data")
    seu_fault_models = DataReader.get_seu_fault_models(data_path)


if __name__ == "__main__":
    main()
