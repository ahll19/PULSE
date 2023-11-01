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
        super().__init__(*args, **kwargs)


class BaseTools:
    @classmethod
    def error_classification(
        cls, seu_log: SeuLog, golden_log: pd.Series, visualize: bool = False
    ) -> Union[pd.Series, Tuple[pd.Series, plt.Figure]]:
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
        # TODO: Maybe add comparison ratio from the article. Issue is number of args
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
        ec = BaseTools.error_classification(seu_log, golden_log)
        ec_onehot = pd.get_dummies(ec)
        n = len(ec)
        rates = ec.value_counts(normalize=True)
        std = ec_onehot.std()
        z = stats.norm.ppf(confidence) / 2
        ci = z * std / n**0.5

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
        n_injection_cycles: int, n_target_bits, n_runs: int
    ) -> float:
        S = n_injection_cycles * n_target_bits
        eps = 1 / S

        x = np.arange(0, n_runs + 1)

        binom = stats.binom.pmf(x, n_runs, eps)
        inner_sum = np.sum(binom[2:] * x[1:-1])

        expectation = S * inner_sum

        return expectation

    @classmethod
    def variance_num_multi_injection_runs(
        cls, n_injection_cycles: int, n_target_bits, n_runs: int
    ) -> float:
        _ = ""
        S = n_injection_cycles * n_target_bits
        eps = 1 / S

        x = np.arange(0, n_runs + 1)

        binom = stats.binom.pmf(x, n_runs, eps)
        y_expect = np.sum(binom[2:] * x[1:-1])

        running_sum = 0

        for j in range(n_runs):
            running_sum += (j - y_expect) ** 2 * binom[j + 1]

        S * running_sum / n_runs
