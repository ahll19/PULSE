from .sections import Data, Coverage, SeuMetaData, ComparisonData, Debug


class RunInfo:
    path: str = None

    data: Data = None
    coverage: Coverage = None
    debug: Debug = None
    seu_metadata: SeuMetaData = None
    comparison_data: ComparisonData = None

    def __init__(self, runinfo_path: str) -> None:
        self.path = runinfo_path
        self.data = Data(runinfo_path)
        self.coverage = Coverage(runinfo_path)
        self.debug = Debug(runinfo_path)
        self.seu_metadata = SeuMetaData(runinfo_path)
        self.comparison_data = ComparisonData(runinfo_path)


if __name__ == "__main__":
    runinfo = RunInfo("ibex_coremark.ini")
