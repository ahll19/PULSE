from enum import StrEnum

from src.firmwares.mappings import MappingMethods


class CoremarkRunInfo(StrEnum):
    # Information for both Golden and SEU run (ends in RunInfo)
    # This is the information we will use to compare against the SEU run
    seed_crc = "seedcrc          : 0x"
    list_crc = "[0]crclist       : 0x"
    matrix_crc = "[0]crcmatrix     : 0x"
    state_crc = "[0]crcstate      : 0x"
    final_crc = "[0]crcfinal      : 0x"
    coremark_score = "CoreMark / MHz: "


class CoremarkSeuRunInfo(StrEnum):
    # Information specific to SEU run (ends in SeuRunInfo)
    # Extending Enums is a pain, so we write the same code twice.
    seed_crc = "seedcrc          : 0x"
    list_crc = "[0]crclist       : 0x"
    matrix_crc = "[0]crcmatrix     : 0x"
    state_crc = "[0]crcstate      : 0x"
    final_crc = "[0]crcfinal      : 0x"
    coremark_score = "CoreMark / MHz: "

    injection_cycle = "Will flip bit at cycle: "
    register = "Forcing value for env.ibex_soc_wrap."
    bit_number = "Fliping bit number: "
    value_before = "Before flip: "
    value_after = "After flip: "


class CoremarkInfoMapper:
    info_to_method_map = {
        CoremarkSeuRunInfo.seed_crc.name: MappingMethods.read_hex_to_int,
        CoremarkSeuRunInfo.list_crc.name: MappingMethods.read_hex_to_int,
        CoremarkSeuRunInfo.matrix_crc.name: MappingMethods.read_hex_to_int,
        CoremarkSeuRunInfo.state_crc.name: MappingMethods.read_hex_to_int,
        CoremarkSeuRunInfo.final_crc.name: MappingMethods.read_hex_to_int,
        CoremarkSeuRunInfo.coremark_score.name: MappingMethods.read_M_to_int,
        CoremarkSeuRunInfo.injection_cycle.name: MappingMethods.read_int,
        CoremarkSeuRunInfo.register.name: MappingMethods.read_str,
        CoremarkSeuRunInfo.bit_number.name: MappingMethods.read_int,
        CoremarkSeuRunInfo.value_before.name: MappingMethods.read_hex_to_int,
        CoremarkSeuRunInfo.value_after.name: MappingMethods.read_hex_to_int,
    }


if __name__ == "__main__":
    pass
