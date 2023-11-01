from abc import ABC, abstractmethod


class BaseError(ABC):
    """
    Base class for error definitions. This class is an abstract base class
    and should not be instantiated.

    The name is used for querying the objects created when we do error classification
    on an object.

    The color is used for plotting consistency. The color should be a valid matplotlib
    color.

    The description is used for printing the error definition to the console. Also for
    looking up specifically what one type of error is classified by.
    """

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
        """
        Used to print the error definition to the console.

        :return: Error definition summary
        :rtype: str
        """
        return f"{self.name} ({self.color})\n{self.description}"

    def __str__(self) -> str:
        """
        When error classes are cast to string types this method is called.

        :return: Error definition summary
        :rtype: str
        """
        return self.__repr__()


class CriticalError(BaseError):
    color = "tab:red"
    name = "Critical Error"
    description = (
        "Logs with missing information are considered critical errors. "
        "(NaN in the seu_log dataframe)"
    )


class DataCorruptionError(BaseError):
    color = "tab:orange"
    name = "Data Corruption Error"
    description = (
        "Logs with different values to the golden log are considered "
        "data corruption errors"
    )


class SilentError(BaseError):
    color = "tab:blue"
    name = "Silent Error"
    description = (
        "Logs where we can't tell the difference from the golden run, "
        "using [COMPARISON_DATA] from the .ini"
    )
