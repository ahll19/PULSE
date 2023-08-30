import os
from src import DataReader


def main():
    data_path = os.path.join(os.getcwd(), "data")
    golden_path = os.path.join(data_path, "golden.txt")
    seu_fault_models = DataReader.get_seu_fault_models(data_path)
    golden_fault_model = DataReader.get_golden_fault_model(golden_path)


if __name__ == "__main__":
    main()
