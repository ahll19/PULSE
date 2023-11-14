from abc import ABC, abstractmethod
from typing import List, Dict

from ....run_info.run_info import RunInfo
from ..node import Node


class BaseOptionalData(ABC):
    run_info: RunInfo = None

    def __init__(self, run_info: RunInfo) -> None:
        self.run_info = run_info

    @abstractmethod
    def get_data_by_run(self, run: str) -> object:
        pass

    def get_data_by_runs(self, runs: List[str]) -> Dict[str, object]:
        return {run: self.get_data_by_run(run) for run in runs}
