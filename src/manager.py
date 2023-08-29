from .log import Golden, Seu, SeuDiff
from typing import Dict, List
import os


class SeuRun:
    seu: Seu = None
    seu_diff: SeuDiff = None

    def __init__(self, seu: Seu, seu_diff: seu_diff) -> None:
        self.seu = seu
        self.seu_diff = seu_diff


class Manager:
    run_names: List[str] = None
    seu_runs: Dict[str, SeuRun] = dict()
    golden_run: Golden = None

    _run_paths: List[str] = None

    def __init__(self, data_path: str) -> None:
        self.run_names = [
            name for name in os.listdir(data_path) if name != "golden.log"
        ]
        self._run_paths = [os.path.join(data_path, name) for name in self.run_names]

        # Make sure all paths exist
        for run_path in self._run_paths:
            if not os.path.exists(run_path):
                raise FileNotFoundError(f"Could not find {run_path}")

        # Create the seu runs
        for name, run_path in zip(self.run_names, self._run_paths):
            seu = Seu(run_path)
            seu_diff = SeuDiff(run_path)
            self.seu_runs[name] = SeuRun(seu, seu_diff)

        # Create the golden run
        self.golden_run = Golden(data_path)
