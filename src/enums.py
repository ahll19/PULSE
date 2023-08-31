from enum import Enum


class RegisterEnum(Enum):
    # Read from XML some time
    big = 1
    small = 2


class ExitValueEnum(Enum):
    normal_exit = 40000000


class InfoEnum(Enum):
    # run info
    injection_clock_cycle = 1
    register = 2
    bit_number = 3
    value_change_before = 4
    value_change_after = 5

    # soft error info
    seedcrc = 6
    listcrc = 7
    matrixcrc = 8
    statecrc = 9
    finalcrc = 10
    coremark_freq = 11


class InfoCastEnum(Enum):
    M_to_int = 1
    str = 2
    int = 3
    hex_to_int = 4
