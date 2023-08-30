from enum import Enum


class RegisterEnum(Enum):  # Should read from the header file which regs are present
    big = 1
    small = 2


class CRCEnum(Enum):
    seed = 1
    list = 2
    matrix = 3
    state = 4
    final = 5

    def __hash__(self) -> int:
        return hash(self.value)
