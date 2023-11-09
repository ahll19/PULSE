from typing import List, Union, Tuple

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
import scipy.stats as stats


from ..data_interface import DataInterface, Node
from ..colorprint import ColorPrinter
from .structures.error_definitions import (
    SilentError,
    DataCorruptionError,
    CriticalError,
    BaseError,
)


class BaseTools:
    @classmethod
    def error_classification(
        cls, data_interface: DataInterface, node: Node, visualize: bool = False
    ) -> Union[pd.Series, Tuple[pd.Series, plt.Figure]]:
        """
        Used to classify the error type in each run of the seu log. The golden run
        object is used to compare against. For definitions of each error see the
        error_definitions.py file, or print out each error object from that same file.
        """
        seu_log = data_interface.get_data_by_node(node)
        golden_log = data_interface.golden_log

        compare_cols = seu_log.columns.intersection(golden_log.index)
        crit_cols = data_interface.run_info.comparison_data.entries
        crit_cols += data_interface.run_info.seu_metadata.entries

        is_critical = seu_log[crit_cols].isna().any(axis=1)
        is_critical.name = CriticalError.name

        is_corruption = seu_log[compare_cols].ne(golden_log).any(axis=1) & ~is_critical
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
        data_interface: DataInterface,
        node: Node,
        injection_time_col: str,
        window_size: int = 150,
        confidence: float = 0.95,
        visualize: bool = False,
    ) -> Union[
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame],
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, plt.figure],
    ]:
        # https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance
        # See Welford's online algorithm for faster implementation of std estimate
        """
        If you SeuLog has an entry corresponding to a time value, this method can be
        used to visualize how that error rate changes over time.

        This method creates an error_classification series based on
        cls.error_classification(), and then uses a window in time to estimate the error
        rate by taking n_error_rate_in_window / n_injection_in_window for each type of
        error.

        The confidence bands are calculated pointwise, to create something akin to
        confidence bands, keep this in mind when interpreting the visualization.
        """
        assert window_size % 2 == 0, "window_size in windowed_error_rate must be even"

        seu_log = data_interface.get_data_by_node(node)
        error_classifications = cls.error_classification(
            data_interface, node, visualize=False
        )

        n = len(error_classifications)
        z = stats.norm.ppf(1 - (1 - confidence) / 2)
        errors = [SilentError.name, DataCorruptionError.name, CriticalError.name]

        df = pd.DataFrame(
            columns=errors,
            data=np.zeros((n, len(errors))),
            index=seu_log[injection_time_col].astype(float),
        ).sort_index()

        conf_lower = df.copy()
        conf_upper = df.copy()

        error_classifications = error_classifications.to_frame()
        error_classifications[injection_time_col] = seu_log.copy()[
            injection_time_col
        ].astype(float)
        error_classifications.sort_values(injection_time_col, inplace=True)
        error_classifications.drop(columns=[injection_time_col], inplace=True)
        error_classifications = error_classifications.squeeze()

        def confidence_and_error_rate(
            error_class: pd.Series, z: float = z, errors: List[BaseError] = errors
        ) -> Tuple[pd.Series, float]:
            _dummies = pd.get_dummies(error_class)
            for _e in errors:
                if _e not in _dummies.columns:
                    _dummies[_e] = np.zeros(len(_dummies)).astype(bool)

            _std = _dummies.std()
            _ci = z * _std / np.sqrt(len(_dummies))
            _dfr = _dummies.sum() / len(_dummies)

            return _dfr, _ci

        ws_2 = window_size // 2
        for i in range(ws_2, n - ws_2):
            rates, ci = confidence_and_error_rate(
                error_class=error_classifications[i - ws_2 : i + ws_2]
            )
            df.iloc[i] = rates
            conf_lower.iloc[i] = rates - ci
            conf_upper.iloc[i] = rates + ci

        if not visualize:
            return df, conf_lower, conf_upper
        cycle = df.index.values.astype(float)
        c = df[CriticalError.name].values
        cl = conf_lower[CriticalError.name].values
        cu = conf_upper[CriticalError.name].values
        d = df[DataCorruptionError.name].values
        dl = conf_lower[DataCorruptionError.name].values
        du = conf_upper[DataCorruptionError.name].values
        s = df[SilentError.name].values
        sl = conf_lower[SilentError.name].values
        su = conf_upper[SilentError.name].values

        fig, ax = plt.subplots()

        y_lims = (-0.1, 1.1)
        alpha = 0.3
        mark_size = 4

        ax.plot(
            cycle,
            c,
            c=CriticalError.color,
            label=CriticalError.name,
            marker=".",
            markersize=mark_size,
        )
        ax.fill_between(cycle, cl, cu, color=CriticalError.color, alpha=alpha)

        ax.plot(
            cycle,
            d,
            c=DataCorruptionError.color,
            label=DataCorruptionError.name,
            marker=".",
            markersize=mark_size,
        )
        ax.fill_between(cycle, dl, du, color=DataCorruptionError.color, alpha=alpha)

        ax.plot(
            cycle,
            s,
            c=SilentError.color,
            label=SilentError.name,
            marker=".",
            markersize=mark_size,
        )
        ax.fill_between(cycle, sl, su, color=SilentError.color, alpha=alpha)

        ax.fill_between(cycle[:ws_2], y_lims[0], y_lims[1], color="grey", alpha=alpha)
        ax.fill_between(
            cycle[n - ws_2 :],
            y_lims[0],
            y_lims[1],
            color="grey",
            alpha=alpha,
            label=r"$\omega/2$",
        )

        ax.set_ylim(y_lims)
        fig.suptitle(r"$\omega=$" + str(window_size))
        fig.legend()
        fig.show()

    @classmethod
    def error_classification_confidence(
        cls,
        data_interface: DataInterface,
        node: Node,
        confidence: float = 0.95,
        visualize: bool = False,
    ) -> Union[pd.Series, Tuple[pd.Series, plt.Figure]]:
        """
        Calculates the confidence intervals for the given error rate estimates.
        """
        seu_log = data_interface.get_data_by_node(node)

        ec = BaseTools.error_classification(data_interface, node, visualize=False)
        ec_onehot = pd.get_dummies(ec)
        n = len(ec)
        rates = ec.value_counts(normalize=True)
        std = ec_onehot.std()
        z = stats.norm.ppf(1 - (1 - confidence) / 2)
        ci = z * std / np.sqrt(n)

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
        cls,
        n_injection_cycles: int,
        n_target_bits,
        n_runs_interval: Tuple[int, int],
        visualize: bool = False,
    ) -> pd.Series | Tuple[pd.Series, plt.figure]:
        """
        More or less the same calculation as the cls.expected_num_multi_injection_runs()
        method, except we calculate the variance of this number of multi-bit run.
        """
        m = np.linspace(*n_runs_interval, 1000)
        n = n_target_bits * n_injection_cycles
        eps = 1 / n
        res = m * (1 - (1 - eps) ** (m - 1))

        res = pd.Series(res, index=m)

        if not visualize:
            return res

        fig, ax = plt.subplots()

        res.plot(ax=ax)
        ylims = ax.get_ylim()
        ax.set_ylim(ylims)

        ax.grid()
        ax.get_xaxis().set_major_formatter(
            mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ","))
        )
        ax.set_xlabel(r"$M$")
        ax.set_ylabel(r"$\mathbb{E}[\Lambda]$")
        ax.set_title(r"$\Lambda$= number of resamples")
        fig.suptitle(r"Number of expected re-samples given $M$ runs")

        return res, fig
