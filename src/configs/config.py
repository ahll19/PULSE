import configparser
import os
from typing import Dict, List


class Config:
    config_dir_path = "src/configs/"
    ini_structure = {
        "STDOUT LOG FILES": [
            "GOLDEN",
            "SEU",
        ],
        "DATA LOADING": [
            "DATA_DIRECTORY",
            "TIMEOUT",
            "MAX_RAM_USAGE",
            "MAX_NUMBER_OF_LOGS",
        ],
        "FIRMWARE": [
            "PATH",
        ],
    }

    possible_configs: Dict[str, str] = None
    config_is_set: bool = False

    # STDOUT LOG FILES
    GOLDEN: str = None
    SEU: str = None

    # DATA LOADING
    DATA_DIRECTORY: str = None
    TIMEOUT: int = None
    MAX_RAM_USAGE: float = None
    MAX_NUMBER_OF_LOGS: int = None

    # FIRMWARE
    PATH: str = None

    def __init__(self, config_name: str = None) -> None:
        if not os.path.isdir(self.config_dir_path):
            err_string = f"Config directory '{self.config_dir_path}' not found.\n"
            err_string += f"Possibly change attribute in {self.__class__.__name__}\n"
            err_string += f"In file {__file__}"
            raise FileNotFoundError(err_string)

        config_paths = [
            os.path.join(self.config_dir_path, file)
            for file in os.listdir(self.config_dir_path)
            if file.endswith(".ini")
        ]

        self.possible_configs = {
            "".join(os.path.basename(path).split(".")[:-1]): path
            for path in config_paths
        }

        if len(self.possible_configs) == 0:
            err_string = f"No config files found in {self.config_dir_path}"
            raise FileNotFoundError(err_string)

        if config_name is not None:
            self.set_config(config_name)
        else:
            print(
                "Config not set. Check possible_configs attribute, and use set_config()"
            )

    def set_config(self, config_name: str) -> None:
        config = configparser.ConfigParser()

        if config_name not in self.possible_configs.keys():
            err_string = f"Config '{config_name}' not found in {self.config_dir_path}"
            raise FileNotFoundError(err_string)

        config.read(self.possible_configs[config_name])

        for section, keys in self.ini_structure.items():
            for key in keys:
                try:
                    value = config[section][key]
                except KeyError:
                    err_string = f"Key '{key}' not found in section '{section}' in "
                    err_string += f"config file '{config_name}'"
                    raise KeyError(err_string)

                if hasattr(self, key):
                    try:
                        value = int(value)
                    except ValueError:
                        pass

                    setattr(self, key, value)
                else:
                    err_string = f"Key '{key}' in section '{section}' in config file "
                    err_string += f"'{config_name}' not found in class "
                    err_string += f"'{self.__class__.__name__}'\n"
                    err_string += f"Add attribute to class, or remove from config file"
                    raise KeyError(err_string)

        self.config_is_set = True
