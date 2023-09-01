from enum import Enum


class SoftErrorIndicatorEnum(Enum):
    seedcrc = 1
    listcrc = 2
    matrixcrc = 3
    statecrc = 4
    finalcrc = 5
    coremark_freq = 6
