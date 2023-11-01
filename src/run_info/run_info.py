from .sections import Data, SeuMetaData, ComparisonData, Debug, OptionalData


class RunInfo:
    path: str = None
    data: Data = None
    coverage: Coverage = None
    debug: Debug = None
    seu_metadata: SeuMetaData = None
    comparison_data: ComparisonData = None
    optional_data: OptionalData = None

    def __init__(self, runinfo_path: str) -> None:
        self.path = runinfo_path
        self.data = Data(runinfo_path)
        self.coverage = Coverage(runinfo_path)
        self.debug = Debug(runinfo_path)
        self.seu_metadata = SeuMetaData(runinfo_path)
        self.comparison_data = ComparisonData(runinfo_path)
        self.optional_data = OptionalData(runinfo_path)


if __name__ == "__main__":
    runinfo = RunInfo("ibex_coremark.ini")
