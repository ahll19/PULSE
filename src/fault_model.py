from typing import Dict, Tuple
from dataclasses import dataclass
from .enums import RegisterEnum, CRCEnum


@dataclass
class SeuDescription:
    clock_cycle: int = None
    # register: RegisterEnum = None
    register: str = None
    bit_number: int = None
    value_change: Tuple[int, int] = None


@dataclass
class SoftError:
    # crc_value_delta: Dict[CRCEnum, int] = None
    # coremark_freq_delta: int = None
    crc_value: Dict[CRCEnum, int] = None
    coremark_freq: int = None


@dataclass
class HardError:
    cpu_stall: bool = None
    bad_exit: bool = None


class FaultDataModel:
    seu_description: SeuDescription = None
    soft_error: SoftError = None
    hard_error: HardError = None

    def __init__(
        self,
        seu_description: SeuDescription,
        soft_error: SoftError,
        hard_error: HardError,
    ) -> None:
        self.seu_description = seu_description
        self.soft_error = soft_error
        self.hard_error = hard_error
