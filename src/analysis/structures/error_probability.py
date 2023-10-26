from .error_definitions import SilentError, DataCorruptionError, CriticalError


class AdjustedErrorProbability:
    silent: float = None
    data_corruption: float = None
    critical: float = None

    w_size: float = None
    n_runs: int = None

    def __init__(
        self,
        silent: float,
        data_corruption: float,
        critical: float,
        w_size: float,
        n_runs: int,
    ) -> None:
        """
        Class used for calculations based on "Avoiding Pitfalls in Fault-Injection Based
        Comparison of Program Susceptibility to Soft Errors" from Horst Schirmeier et al

        For now it is a simple data-object for saving the results of the calculations.

        It might be interesting to add functionality to the class itself to do the
        comparison analysis based on the article.

        :param silent: Adjusted error probability for silent errors
        :type silent: float
        :param data_corruption: Adjusted error probability for data corruption errors
        :type data_corruption: float
        :param critical: Adjusted error probability for critical errors
        :type critical: float
        :param w_size: Size of the injection space (i.e. n_bits * n_cycles)
        :type w_size: float
        :param n_runs: Number of SEU runs carried out and used for calculation
        :type n_runs: int
        """
        self.silent = silent
        self.data_corruption = data_corruption
        self.critical = critical

        self.w_size = w_size
        self.n_runs = n_runs
