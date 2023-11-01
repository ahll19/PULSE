from .sections import Data, SeuMetaData, ComparisonData, Debug, OptionalData


class RunInfo:
    path: str = None
    data: Data = None
    debug: Debug = None
    seu_metadata: SeuMetaData = None
    comparison_data: ComparisonData = None
    optional_data: OptionalData = None

    def __init__(self, runinfo_path: str) -> None:
        """
        Interface for the runinfo file.

        Only the runinfo file path is needed, since all the logic of how sections are
        handled is specified in the sections themselves.

        There could be added logic here for custom sections, if one wishes to do so.
        I recommend adding a new file called custom_sections (or similar), and importing
        it through there. If done so one should add an if-statement to check if the
        custom section is present, and then add it if this is the case (as to not break
        functionality for people without this custom section)

        :param runinfo_path: path to the runinfo file, these are the *.ini files in the
        same folder as ths file.
        :type runinfo_path: str
        """
        self.path = runinfo_path
        self.data = Data(runinfo_path)
        self.debug = Debug(runinfo_path)
        self.seu_metadata = SeuMetaData(runinfo_path)
        self.comparison_data = ComparisonData(runinfo_path)
        self.optional_data = OptionalData(runinfo_path)


if __name__ == "__main__":
    runinfo = RunInfo("ibex_coremark.ini")
