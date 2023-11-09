from .ibex_coremark_tools import IbexCoremarkTools
from .structures.seu_log import SeuLog
from ..data_interface import DataInterface, Node
from .structures.error_definitions import (
    SilentError,
    DataCorruptionError,
    CriticalError,
)

from typing import Union, Tuple

import matplotlib.pyplot as plt
import pandas as pd


class IbexHwsecCoremarkTools(IbexCoremarkTools):
    @classmethod
    def alert_classification(
        cls, data_interface: DataInterface, node: Node, visualize: bool = False
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, plt.Figure]]:
        seu_log = data_interface.get_data_by_node(node)
        golden_log = data_interface.golden_log
        error_classifications = cls.error_classification(data_interface, node, False)

        critical_error = error_classifications == CriticalError.name
        corruption_error = error_classifications == DataCorruptionError.name
        silent_error = error_classifications == SilentError.name

        alert_series = seu_log["alert_val"] != 0
        alert_series = alert_series.astype(int)

        alert_heights = [
            alert_series[critical_error].sum(),
            alert_series[corruption_error].sum(),
            alert_series[silent_error].sum(),
        ]

        critical_error = critical_error.astype(int)
        corruption_error = corruption_error.astype(int)
        silent_error = silent_error.astype(int)

        time_index = seu_log["injection_cycle"].astype(float)

        df = pd.DataFrame(
            {
                CriticalError.name: critical_error,
                DataCorruptionError.name: corruption_error,
                SilentError.name: silent_error,
                "injection_cycle": time_index,
                "alert": alert_series,
            }
        )
        if not visualize:
            return df

        fig, ax = plt.subplots()
        error_heights = [
            critical_error.sum(),
            corruption_error.sum(),
            silent_error.sum(),
        ]
        [a / e for a, e in zip(alert_series, error_heights)]
        is_log = max(error_heights) > 10 * min(error_heights)

        # Making a helper df to plot multi-bars
        df_plot = pd.DataFrame(
            {
                "Error class": error_heights,
                "Alert signal": alert_heights,
            },
            index=[CriticalError.name, DataCorruptionError.name, SilentError.name],
        )

        df_plot.plot.bar(
            ax=ax,
            log=is_log,
            color=[CriticalError.color, DataCorruptionError.color, SilentError.color],
        )

        # Insert # of runs on to bar
        for container in ax.containers:
            ax.bar_label(container)
        ax.legend()

        if is_log:
            ax.set_ylim(bottom=1)

        ax.set_title(f"Error Classification with alerts: {seu_log.name}")
        ax.set_ylabel("Number of errors")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

        fig.tight_layout()
        fig.show()

        return df, fig
