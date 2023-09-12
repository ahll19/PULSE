from typing import List, Tuple, Union

import pandas as pd
import numpy as np

from .enums import RunInfoEnum
from .register_tree import Node
from .data_reader import DataReader


class Analyses:
    # extra descriptors used by the different methods to unify column names and such
    failed_to_parse_column = "failed to parse"
    silent_column = "silent"
    parsed_column = "parsed"

    @classmethod
    def check_inputs(
        cls, data: pd.DataFrame, masking_series: pd.Series, golden_log: pd.Series
    ) -> bool:
        if data is None or masking_series is None or golden_log is None:
            return False

        if len(data) == 0 or len(masking_series) == 0 or len(golden_log) == 0:
            return False

        return True

    @classmethod
    def binary_error_series(
        cls, data: pd.DataFrame, masking_series: pd.Series, golden_log: pd.Series
    ) -> Union[None, pd.Series]:
        valid_inputs = cls.check_inputs(data, masking_series, golden_log)
        if not valid_inputs:
            return None

        binary_error_table_by_type = cls.binary_error_table_by_type(
            data, masking_series, golden_log
        )

        result = binary_error_table_by_type.sum(axis=1).astype(bool)

        if result is None or not isinstance(result, pd.Series):
            _ = "breakpoint"

        return result

    @classmethod
    def binary_error_table_by_type(
        cls, data: pd.DataFrame, masking_series: pd.Series, golden_log: pd.Series
    ) -> Union[None, pd.DataFrame]:
        valid_inputs = cls.check_inputs(data, masking_series, golden_log)
        if not valid_inputs:
            return None

        common_columns = data.columns.intersection(golden_log.index)
        diff_frame = data[common_columns] != golden_log
        diff_frame[cls.failed_to_parse_column] = ~masking_series

        if diff_frame is None or (not isinstance(diff_frame, pd.DataFrame)):
            _ = "breakpoint"

        return diff_frame

    @classmethod
    def error_rate(
        cls, data: pd.DataFrame, masking_series: pd.Series, golden_log: pd.Series
    ) -> Union[None, float]:
        valid_inputs = cls.check_inputs(data, masking_series, golden_log)
        if not valid_inputs:
            return None

        error_series = cls.binary_error_series(data, masking_series, golden_log)
        result = error_series.sum() / len(error_series)

        if result is None or not isinstance(result, float):
            _ = "breakpoint"

        return result

    @classmethod
    def error_rate_by_type(
        cls, data: pd.DataFrame, masking_series: pd.Series, golden_log: pd.Series
    ) -> Union[None, pd.Series]:
        valid_inputs = cls.check_inputs(data, masking_series, golden_log)
        if not valid_inputs:
            return None

        error_table = cls.binary_error_table_by_type(data, masking_series, golden_log)
        result = error_table.sum(axis=0) / len(error_table)

        if result is None or not isinstance(result, pd.Series):
            _ = "breakpoint"

        return result

    @classmethod
    def error_rate_over_time(
        cls,
        data: pd.DataFrame,
        masking_series: pd.Series,
        golden_log: pd.Series,
        window_size: int,
    ) -> pd.DataFrame:
        valid_inputs = cls.check_inputs(data, masking_series, golden_log)
        if not valid_inputs:
            return None

        injection_time_series = data[RunInfoEnum.injection_cycle.name]

        parsed_err_series = cls.binary_error_series(data, masking_series, golden_log)
        unparsed_err_series = ~(masking_series.copy())
        silent_series = ~(parsed_err_series | unparsed_err_series)

        result = pd.DataFrame(
            {
                cls.parsed_column: parsed_err_series,
                cls.failed_to_parse_column: unparsed_err_series,
                cls.silent_column: silent_series,
            }
        )

        result[RunInfoEnum.injection_cycle.name] = injection_time_series
        result.sort_values(by=RunInfoEnum.injection_cycle.name, inplace=True)

        for col in [cls.parsed_column, cls.failed_to_parse_column, cls.silent_column]:
            result[col] = result[col].rolling(window_size).mean()

        result.dropna(inplace=True)

        if result is None or not isinstance(result, pd.Series):
            _ = "breakpoint"

        return result
