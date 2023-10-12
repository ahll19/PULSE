from enum import StrEnum

from src.firmwares.mappings import MappingMethods


class RunInfo(StrEnum):
    # Information for both Golden and SEU run (ends in RunInfo)
    # This is the information we will use to compare against the SEU run
    seed_crc = "seedcrc          : 0x"
    list_crc = "[0]crclist       : 0x"
    matrix_crc = "[0]crcmatrix     : 0x"
    state_crc = "[0]crcstate      : 0x"
    final_crc = "[0]crcfinal      : 0x"
    coremark_score = "CoreMark / MHz: "


class SeuRunInfo(StrEnum):
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

    # Ibex alert signals extracted in simulator through VPI
    alert_minor = "alert_minor_o: "
    alert_major_bus = "alert_major_bus_o: "
    alert_major_internal = "alert_major_internal_o: "

class InfoMapper:
    info_to_method_map = {
        SeuRunInfo.seed_crc.name: MappingMethods.read_hex_to_int,
        SeuRunInfo.list_crc.name: MappingMethods.read_hex_to_int,
        SeuRunInfo.matrix_crc.name: MappingMethods.read_hex_to_int,
        SeuRunInfo.state_crc.name: MappingMethods.read_hex_to_int,
        SeuRunInfo.final_crc.name: MappingMethods.read_hex_to_int,
        SeuRunInfo.coremark_score.name: MappingMethods.read_M_to_int,
        SeuRunInfo.injection_cycle.name: MappingMethods.read_int,
        SeuRunInfo.register.name: MappingMethods.read_str,
        SeuRunInfo.bit_number.name: MappingMethods.read_int,
        SeuRunInfo.value_before.name: MappingMethods.read_hex_to_int,
        SeuRunInfo.value_after.name: MappingMethods.read_hex_to_int,
        SeuRunInfo.alert_minor.name : MappingMethods.read_int,
        SeuRunInfo.alert_major_bus.name : MappingMethods.read_int,
        SeuRunInfo.alert_major_internal.name : MappingMethods.read_int
    }


if __name__ == "__main__":
    pass
