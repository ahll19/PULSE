# Perhaps create a base seu class
from typing import List
import os


class Seu:
    raw_lines: List[str] = []
    clean_lines: List[str] = []

    def __init__(self, run_path: str) -> None:
        file_path = os.path.join(run_path, "log.txt")

        # check that the path exists, and that it contains a log.txt file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not find {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not find {file_path}")

        # read the log file into raw_lines
        with open(file_path, "r") as f:
            self.raw_lines = f.readlines()

        # Clean up lines
        self.generate_and_set_clean_lines()

    def generate_and_set_clean_lines(self) -> None:
        _tmp_lines = self.raw_lines.copy()

        _tmp_lines = [line.replace("\n", "") for line in _tmp_lines]
        _tmp_lines = [line for line in _tmp_lines if len(line) > 1]

        _tmp_lines = self._rm_before_seu(_tmp_lines)
        _tmp_lines = self._clean_lines_patterns(_tmp_lines)

    def _rm_before_seu(self, raw_lines_copy: List[str]) -> List[str]:
        clean = []
        should_append = False

        for line in raw_lines_copy:
            if "UVM Doing fault injection." == line:
                should_append = True

            if not should_append:
                continue

            clean.append(line)

        return clean

    def _clean_lines_patterns(self, raw_lines_copy: List[str]) -> List[str]:
        clean_lines = []
        line_rm_by_beginning = [
            "Cannot find VPI signal",
            "UVM_WARNING",
            "UVM_WARNING @ 0 s: reporter [TPRGED] Type name '",
        ]
        line_rm_by_ending = []
        line_rm_by_total = [
            "Name  Type  Size  Value",
            "-----------------------",
            "env   env   -     -",
        ]

        for line in raw_lines_copy:
            if any([line.startswith(beginning) for beginning in line_rm_by_beginning]):
                continue
            if any([line.endswith(ending) for ending in line_rm_by_ending]):
                continue
            if any([line == total for total in line_rm_by_total]):
                continue
            clean_lines.append(line)

        return clean_lines
