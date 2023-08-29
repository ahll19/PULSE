import os
from src import Manager


def main():
    data_path = os.path.join(os.getcwd(), "data")
    manager = Manager(data_path=data_path)

    k = 10

    for run_name, seu_run in manager.seu_runs.items():
        print(f"Run name: {run_name}")
        print(f"Seu: {seu_run.seu.raw_lines[:k]}")
        print(f"Seu diff: {seu_run.seu_diff.raw_lines[:k]}")
        print()


if __name__ == "__main__":
    main()
