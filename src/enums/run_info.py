from enum import Enum


class RunInfoEnum(Enum):
    injection_cycle = 1
    register = 2
    bit_number = 3
    value_before = 4
    value_after = 5
    seed_crc = 6
    list_crc = 7
    matrix_crc = 8
    state_crc = 9
    final_crc = 10
    coremark_score = 11
