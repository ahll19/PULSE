# Perhaps create a base seu class
from typing import List
import os


class SeuDiff:
    raw_lines: List[str] = []

    def __init__(self, run_path: str) -> None:
        file_path = os.path.join(run_path, "diff.log")

        # check that the path exists, and that it contains a diff.log file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not find {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not find {file_path}")

        # read the log file into raw_lines
        with open(file_path, "r") as f:
            self.raw_lines = f.readlines()
