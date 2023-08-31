from enum import Enum


class SeuDescriptionEnum(Enum):
    injection_clock_cycle = 1
    register = 2
    bit_number = 3
    value_change_before = 4
    value_change_after = 5
