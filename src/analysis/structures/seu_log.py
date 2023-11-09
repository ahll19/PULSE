import pandas as pd


class SeuLog(pd.DataFrame):
    name: str = ""

    def __init__(self, *args, **kwargs) -> None:
        """
        Wrapper class for the pandas dataframe. This is just to add the attribute name
        for now, but we could extend this class to be able to do summaries or similar.

        All SEU log dataframes should be wrapped in this class.
        """
        super().__init__(*args, **kwargs)
