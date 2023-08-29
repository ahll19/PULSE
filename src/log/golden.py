from typing import List
import pandas as pd
import os
import re
from time import time as curr_time


class Golden:
    raw_lines: List[str] = []
    log_dataframe: pd.DataFrame = None
    read_timeout: int = 30  # 30 second timeout on reading the golden.log file

    def __init__(self, data_path: str) -> None:
        file_path = os.path.join(data_path, "golden.log")

        # check that the path exists, and that it contains a golden.log file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not find {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not find {file_path}")

        # read the golden.log file into raw_lines
        print("Reading golden.log file")
        with open(file_path, "r") as f:
            start_time = curr_time()
            while curr_time() < start_time + self.read_timeout:
                line = f.readline()
                if line == "":
                    break

                self.raw_lines.append(line)

        # Read the pandas frame, not smart right now with the formatting
        raw_lines = []
        header = [word.strip() for word in self.raw_lines[0].split("\t")]
        for line in self.raw_lines[1:-1]:
            words = line.split("\t")
            new_words = []
            for word in words:
                new_words.append(word.strip())
            new_words[-2:] = [new_words[-2] + " " + new_words[-1]]
            raw_lines.append(new_words)

        self.log_dataframe = pd.DataFrame(raw_lines, columns=header)
