import configparser
from typing import List


class Data:
    directory: str = None
    golden: str = None
    seu: str = None
    vpi: str = None
    timeout: int = None
    max_ram_usage: int = None
    max_number_logs: int = None
    cpu_cycles : int = None

    def __init__(self, runinfo_path: str) -> None:
        """
        Initializes the Data section of the runinfo file.

        Data contains information about where the parser should look for specific files,
        and other settings regarding to parsin the data, such as timeout.

        All variables of this class are hard-coded, and as such must be present in
        the config file.

        :param runinfo_path: path to the runinfo file, these are the *.ini files in the
        same folder as ths file.
        :type runinfo_path: str
        """
        config = configparser.ConfigParser()
        config.read(runinfo_path)

        self.directory = str(config["DATA"]["directory"])
        self.golden = str(config["DATA"]["golden"])
        self.seu = str(config["DATA"]["seu"])
        self.vpi = str(config["DATA"]["vpi"])
        self.timeout = int(config["DATA"]["timeout"])
        self.read_optional = bool(int(config["DATA"]["read_optional"]))
        self.cpu_cyles = int(config["DATA"]["cpu_cycles"])

        if self.timeout != -1 and self.timeout < 0:
            raise ValueError(
                "Timeout in config is negative, and -1. Check your ini file."
            )


class Debug:
    error_utf_parsing: bool = None
    percent_failed_reads: bool = None
    percent_register_tree_populated: bool = None
    loading_bar_on_data_parsing: bool = None

    def __init__(self, runinfo_path: str) -> None:
        """
        Initializes the Debug section of the runinfo file.

        Debug is used to turn on/off certain debug features of the parser. if all
        features in the ini file are turned off nothing will be printed to the console.

        :param runinfo_path: path to the runinfo file, these are the *.ini files in the
        same folder as ths file.
        :type runinfo_path: str
        """
        config = configparser.ConfigParser()
        config.read(runinfo_path)

        self.error_utf_parsing = bool(int(config["DEBUG"]["error_utf_parsing"]))
        self.percent_failed_reads = bool(int(config["DEBUG"]["percent_failed_reads"]))
        self.percent_register_tree_populated = bool(
            int(config["DEBUG"]["percent_register_tree_populated"])
        )
        self.loading_bar_on_data_parsing = bool(
            int(config["DEBUG"]["loading_bar_on_data_parsing"])
        )


class SeuMetaData:
    entries: List[str] = None
    register: str = None
    register_delimiter: str = None

    def __init__(self, runinfo_path: str) -> None:
        """
        Initializes the SeuMetaData section of the runinfo file.

        SeuMetaData is used to specify which lines in the log file should be parsed and
        define the SEU run. There MUST be a "register" and
        "register_delimiter" entry in the ini file, as these are used to parse the log
        and structure the data-tree. These registers and delimiters must match across
        the [DATA][vpi] file, and the log file lines.

        All other information than the hard coded register and register_delimiter are
        used to specify information about the SEU run, such as when it was run, and
        what the register values were before and after the injection.

        These lines are among those that will be pattern-matched against the logfile.

        Example:
        the logs contain the line
            Will flip bit at cycle: xxxx
        and we want to save xxxx. We then write the following in the ini file:
            injection_cycle=Will flip bit at cycle:
        which will save whatever came after this pattern match, in this case xxxx.

        Make sure that the pattern match will only match one line in the log file,
        since the first matching line encountered will be used for the meta-data.

        :param runinfo_path: path to the runinfo file, these are the *.ini files in the
        same folder as ths file.
        :type runinfo_path: str
        """
        self.entries = []

        config = configparser.ConfigParser()
        config.read(runinfo_path)

        # making sure register is present, along with register_delimiter
        # If you get an error here make sure those entries are present in the ini file
        # under the SEU_METADATA section
        self.register = str(config["SEU_METADATA"]["register"])
        self.register_delimiter = str(config["SEU_METADATA"]["register_delimiter"])

        for key, value in config["SEU_METADATA"].items():
            setattr(self, key, value)
            self.entries.append(key)


class ComparisonData:
    entries: List[str] = None

    def __init__(self, runinfo_path: str) -> None:
        """
        Initializes the ComparisonData section of the runinfo file.

        ComparisonData is used to specify which lines in the log file should be parsed
        and define the golden run. Lines in this section are pattern matched as in
        SeuMetaData. Lines specified here must be present, identically, both in the SEU
        runs and in the golden run. No entries are hardcoded in this section.

        Example:
        the logs contain the line
            calculation result: xxxx
        and we want to this line. We then write the following in the ini file:
            calculation_result=calculation result:

        Values in this section are used to define data-corruption-errors


        :param runinfo_path: path to the runinfo file, these are the *.ini files in the
        same folder as ths file.
        :type runinfo_path: str
        """
        self.entries = []

        config = configparser.ConfigParser()
        config.read(runinfo_path)

        for key, value in config["COMPARISON_DATA"].items():
            setattr(self, key, value)
            self.entries.append(key)


# class OptionalData:
#     entries: List[str] = None
#     read_optional: bool = None

#     def __init__(self, runinfo_path: str) -> None:
#         self.entries = []

#         config = configparser.ConfigParser()
#         config.read(runinfo_path)

#         for key, value in config["OPTIONAL_DATA"].items():
#             setattr(self, key, value)
#             self.entries.append(key)
