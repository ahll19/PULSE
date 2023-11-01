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

    def __init__(self, runinfo_path: str) -> None:
        config = configparser.ConfigParser()
        config.read(runinfo_path)

        self.directory = str(config["DATA"]["directory"])
        self.golden = str(config["DATA"]["golden"])
        self.seu = str(config["DATA"]["seu"])
        self.vpi = str(config["DATA"]["vpi"])
        self.timeout = int(config["DATA"]["timeout"])
        self.read_optional = bool(int(config["DATA"]["read_optional"]))

class Coverage:
    n_cycles: int = None
    n_bits: int = None

    def __init__(self, runinfo_path: str) -> None:
        config = configparser.ConfigParser()
        config.read(runinfo_path)

        self.n_cycles = int(config["COVERAGE"]["n_cycles"])
        self.n_bits = int(config["COVERAGE"]["n_bits"])


class Debug:
    error_utf_parsing: bool = None
    percent_failed_reads: bool = None
    percent_register_tree_populated: bool = None

    def __init__(self, runinfo_path: str) -> None:
        config = configparser.ConfigParser()
        config.read(runinfo_path)

        self.error_utf_parsing = bool(int(config["DEBUG"]["error_utf_parsing"]))
        self.percent_failed_reads = bool(int(config["DEBUG"]["percent_failed_reads"]))
        self.percent_register_tree_populated = bool(
            int(config["DEBUG"]["percent_register_tree_populated"])
        )


class SeuMetaData:
    entries: List[str] = None
    register: str = None
    register_delimiter: str = None

    def __init__(self, runinfo_path: str) -> None:
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
        self.entries = []

        config = configparser.ConfigParser()
        config.read(runinfo_path)

        for key, value in config["COMPARISON_DATA"].items():
            setattr(self, key, value)
            self.entries.append(key)


class OptionalData:
    entries: List[str] = None
    read_optional : bool = None

    def __init__(self, runinfo_path: str) -> None:
        self.entries = []

        config = configparser.ConfigParser()
        config.read(runinfo_path)

        for key, value in config["OPTIONAL_DATA"].items():
            setattr(self, key, value)
            self.entries.append(key)