from typing import Union, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.stats as stats

from .structures import (
    SilentError,
    DataCorruptionError,
    CriticalError,
    AdjustedErrorProbability,
)


class SeuLog(pd.DataFrame):
    name: str = ""

    def __init__(self, *args, **kwargs) -> None:
        """
        Wrapper class for the pandas dataframe. This is just to add the attribute name
        for now, but we could extend this class to be able to do summaries or similar.

        All SEU log dataframes should be wrapped in this class.
        """
        super().__init__(*args, **kwargs)


class BaseTools:
    @classmethod
    def error_classification(
        cls, seu_log: SeuLog, golden_log: pd.Series, visualize: bool = False
    ) -> Union[pd.Series, Tuple[pd.Series, plt.Figure]]:
        """
        Used to classify the error type in each run of the seu log. The golden run
        object is used to compare against. For definitions of each error see the
        error_definitions.py file, or print out each error object from that same file.

        :param seu_log: SeuLog of a given run. Can be queried from the DataInterface
        object, by usign a node.
        :type seu_log: SeuLog
        :param golden_log: Series showing the information parsed from the golden run.
        can be found on the golden_log attribute of the DataInterface class.
        :type golden_log: pd.Series
        :param visualize: Whether or not to visualize the results, defaults to False
        :type visualize: bool, optional
        :return: Returns the error classifications in a series. The string values of the
        series are defined by the Error objects' names. If visualize==True this method
        also returns the figure object from the visualization.
        :rtype: Union[pd.Series, Tuple[pd.Series, plt.Figure]]
        """
        cols = seu_log.columns.intersection(golden_log.index)

        is_critical = seu_log.isna().any(axis=1)
        is_critical.name = CriticalError.name

        is_corruption = seu_log[cols].ne(golden_log).any(axis=1) & ~is_critical
        is_corruption.name = DataCorruptionError.name

        is_silent = ~(is_critical | is_corruption)
        is_silent.name = SilentError.name

        error_class = pd.Series([None] * len(seu_log), index=seu_log.index)
        error_class[is_critical] = CriticalError.name
        error_class[is_corruption] = DataCorruptionError.name
        error_class[is_silent] = SilentError.name

        if not visualize:
            return error_class

        fig, ax = plt.subplots()
        heights = [is_critical.sum(), is_corruption.sum(), is_silent.sum()]
        is_log = max(heights) > 10 * min(heights)
        ax.bar(
            x=[CriticalError.name, DataCorruptionError.name, SilentError.name],
            height=heights,
            color=[CriticalError.color, DataCorruptionError.color, SilentError.color],
            log=is_log,
        )
        if is_log:
            ax.set_ylim(bottom=1)

        ax.set_title(f"Error Classification: {seu_log.name}")
        ax.set_ylabel("Number of errors")

        fig.tight_layout()
        fig.show()

        return error_class, fig

    @classmethod
    def windowed_error_rate(
        cls,
        seu_log: SeuLog,
        golden_log: pd.Series,
        injection_time_col: str,
        window_size: int = 1000,
        visualize: bool = False,
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, plt.figure]]:
        """
        If you SeuLog has an entry corresponding to a time value, this method can be
        used to visualize how that error rate changes over time.

        This method creates an error_classification series based on
        cls.error_classification(), and then uses a window in time to estimate the error
        rate by taking n_error_rate_in_window / n_injection_in_window for each type of
        error.

        :param seu_log: SeuLog of a given run. Can be queried from the DataInterface
        object, by usign a node.
        :type seu_log: SeuLog
        :param golden_log: Series showing the information parsed from the golden run.
        can be found on the golden_log attribute of the DataInterface class.
        :type golden_log: pd.Series
        :param injection_time_col: Name of column in SeuLog which corresponds to the
        time value. Make sure only numerical data is present in this column.
        :type injection_time_col: str
        :param window_size: How large of a window to use, defaults to 1000
        :type window_size: int, optional
        :param visualize: whether or not to visualize the results, defaults to False
        :type visualize: bool, optional
        :return: Returns a dataframe with error rates for all types. If
        visualize==True also returns the figure used for visualization.
        :rtype: Union[pd.DataFrame, Tuple[pd.DataFrame, plt.figure]]
        """
        error_classifications = cls.error_classification(seu_log, golden_log, False)

        silent_error = error_classifications == SilentError.name
        silent_error = silent_error.astype(int)
        corruption_error = error_classifications == DataCorruptionError.name
        corruption_error = corruption_error.astype(int)
        critical_error = error_classifications == CriticalError.name
        critical_error = critical_error.astype(int)

        time_index = seu_log[injection_time_col].astype(float)

        df = pd.DataFrame(
            {
                SilentError.name: silent_error,
                DataCorruptionError.name: corruption_error,
                CriticalError.name: critical_error,
                injection_time_col: time_index,
            }
        )
        df = df.set_index(injection_time_col).sort_index()
        df = df.rolling(window_size, min_periods=1).mean()

        if not visualize:
            return df

        fig, ax = plt.subplots()

        ax.stackplot(
            df.index,
            df[SilentError.name],
            df[DataCorruptionError.name],
            df[CriticalError.name],
            labels=[SilentError.name, DataCorruptionError.name, CriticalError.name],
            colors=[SilentError.color, DataCorruptionError.color, CriticalError.color],
        )
        ax.legend(loc="upper left")
        ax.set_title(f"Windowed Error Rate: {seu_log.name}")
        ax.set_ylabel("Error Rate")
        ax.set_xlabel(injection_time_col)

        fig.tight_layout()
        fig.show()

        return df, fig

    @classmethod
    def adjusted_probability(
        cls, seu_log: SeuLog, golden_log: pd.Series, n_cycles: int, n_bits: int
    ) -> AdjustedErrorProbability:
        """
        Horst Schirmeier et al proposed in their article "Avoiding Pitfalls in
        Fault-Injection Based Comparison of Program Susceptibility to Soft Errors" that
        normal methods for comparing the resilience of different SoC designs have some
        pitfalls. This method is creating an adjusted calculation based on what was
        proposed in that article

        :param seu_log: SeuLog of a given run. Can be queried from the DataInterface
        object, by usign a node.
        :type seu_log: SeuLog
        :param golden_log: Series showing the information parsed from the golden run.
        can be found on the golden_log attribute of the DataInterface class.
        :type golden_log: pd.Series
        :param n_cycles: Number of cycles present in the simulation
        :type n_cycles: int
        :param n_bits: Number of bits the simulator can inject on
        :type n_bits: int
        :return: A custom object with attributes which are results of the adjusted
        calculation
        :rtype: AdjustedErrorProbability
        """

        w = n_bits * n_cycles
        n = len(seu_log)
        classification = cls.error_classification(seu_log, golden_log, False)

        n_silent = (classification == SilentError.name).sum()
        n_corruption = (classification == DataCorruptionError.name).sum()
        n_critical = (classification == CriticalError.name).sum()

        silent = w * n_silent / n
        corruption = w * n_corruption / n
        critical = w * n_critical / n

        return AdjustedErrorProbability(silent, corruption, critical, w, n)

    @classmethod
    def error_classification_confidence(
        cls,
        seu_log: SeuLog,
        golden_log: pd.Series,
        confidence: float = 0.95,
        visualize: bool = False,
    ) -> Union[pd.Series, Tuple[pd.Series, plt.Figure]]:
        """
        Calculates the confidence intervals for the given error rate estimates. For more
        details on the technical formulation of this see the docs folder

        :param seu_log: SeuLog of a given run. Can be queried from the DataInterface
        object, by usign a node.
        :type seu_log: SeuLog
        :param golden_log: Series showing the information parsed from the golden run.
        can be found on the golden_log attribute of the DataInterface class.
        :type golden_log: pd.Series
        :param confidence: Confidence level, 0.95-> 95% confidence that the true
        parameter (actual error rate) is in the calculated interval, defaults to 0.95
        :type confidence: float, optional
        :param visualize: Whether or not to visualize the results, defaults to False
        :type visualize: bool, optional
        :return: Returns the size of the confidence intervals of error rate estimates.
        If visualize==True also returns the figure object created by the visualization.
        :rtype: Union[pd.Series, Tuple[pd.Series, plt.Figure]]
        """
        ec = BaseTools.error_classification(seu_log, golden_log)
        ec_onehot = pd.get_dummies(ec)
        n = len(ec)
        rates = ec.value_counts(normalize=True)
        std = ec_onehot.std()
        z = stats.norm.ppf(1 - (1 - confidence) / 2)
        ci = z * std

        if not visualize:
            return ci * 2

        name_list = [CriticalError.name, DataCorruptionError.name, SilentError.name]
        fig, ax = plt.subplots()
        fig.suptitle(f"#Samples: {n}")
        ax.bar(
            rates[name_list].index,
            rates[name_list],
            color=[CriticalError.color, DataCorruptionError.color, SilentError.color],
        )
        ax.errorbar(
            rates[name_list].index,
            rates[name_list],
            yerr=ci[name_list],
            fmt="none",
            ecolor="black",
            capsize=5,
        )
        ylim_top = ax.get_ylim()[1]
        text_height = ylim_top * 0.95
        ax.set_ylim(top=ylim_top * 1.05)

        for i, name in enumerate(name_list):
            text = f"$\sigma={{{std[name]:.1e}}}$\n"
            text += f"CI size: {2*ci[name]:.1e}\n"
            ax.text(i - 0.2, text_height, text, color="black")

        ax.set_title(f"Error Classification: {seu_log.name}")
        fig.show()

        return ci * 2, fig

    @classmethod
    def expected_num_multi_injection_runs(
        cls, n_injection_cycles: int, n_target_bits, n_runs: int
    ) -> float:
        """
        More or less the same calculation as the cls.expected_num_multi_injection_runs()
        method, except we calculate the variance of this number of multi-bit run.

        For more mathematical detail on both of these methods refer to the docs folder

        """
        pass
