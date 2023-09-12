from enum import Enum


class GoldenRunInfoEnum(Enum):
    seed_crc = 1
    list_crc = 2
    matrix_crc = 3
    state_crc = 4
    final_crc = 5
    coremark_score = 6
