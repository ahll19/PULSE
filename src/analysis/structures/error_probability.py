from .error_definitions import SilentError, DataCorruptionError, CriticalError


class AdjustedErrorProbability:
    silent: float = None
    data_corruption: float = None
    critical: float = None

    w_size: float = None  # Size of the injection space
    n_runs: int = None  # Number of runs to average over

    def __init__(
        self,
        silent: float,
        data_corruption: float,
        critical: float,
        w_size: float,
        n_runs: int,
    ) -> None:
        self.silent = silent
        self.data_corruption = data_corruption
        self.critical = critical

        self.w_size = w_size
        self.n_runs = n_runs
