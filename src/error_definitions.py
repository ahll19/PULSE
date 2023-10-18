from abc import ABC, abstractmethod


class Error(ABC):
    @property
    @abstractmethod
    def color(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    def __repr__(self) -> str:
        return f"{self.name} ({self.color})\n{self.description}"

    def __str__(self) -> str:
        return self.__repr__()


class CriticalError(Error):
    color = "red"
    name = "Critical Error"
    description = (
        "Logs with missing information are considered critical errors. "
        "(NaN in the seu_log dataframe)"
    )


class DataCorruptionError(Error):
    color = "orange"
    name = "Data Corruption Error"
    description = (
        "Logs with different values to the golden log are considered "
        "data corruption errors"
    )


class SilentError(Error):
    color = "blue"
    name = "Silent Error"
    description = (
        "Logs where we can't tell the difference from the golden run, "
        "using [COMPARISON_DATA] from the .ini"
    )
