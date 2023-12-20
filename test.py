from src.data_interface import DataInterface
from src.run_info.run_info import RunInfo
from src.analysis.base_tools import BaseTools
from src.analysis.structures.error_definitions import SilentError
from src.colorprint import ColorPrinter as cp

import pandas as pd

run_info_path = "src/run_info/ibex_hwsec_coremark.ini"
number_of_registers = 32
register_file_name = "register_file_i"
seu_injection_cycle_column = "injection_cycle"
seed_column = "uvm_seed"
bit_number_column = "bit_number"

seu_injection_flip_register = True
inject_intervals_path = "/home/anders/Git/prunev/golden_trace_encoding.csv"
inject_intervals_index_column = "Cycle"

save_false_negatives = False
save_injection_interval_assumption = True

if __name__ == "__main__":
    # ==================================================================================
    # Prepare data
    # ==================================================================================
    run_info = RunInfo(run_info_path)
    data_interface = DataInterface(run_info)

    def time_fixer(x: str):
        x = int(x)
        mod = x % 5
        if mod == 0:
            return (x + 20) / 10 - 1
        else:
            return (x + (5 - mod) + 20) / 10 - 1

    nans = data_interface.seu_log["injection_cycle"].isna()
    data_interface.seu_log["injection_cycle"] = data_interface.seu_log[
        "injection_cycle"
    ][~nans].apply(time_fixer)

    node = data_interface.get_node_by_name(register_file_name)[0]
    node_seu_logs = data_interface.get_seu_log_by_node(node)
    cp.print_bold(f"Number of SEU logs on register file: {len(node_seu_logs)}")
    print()
    error_classification = BaseTools.error_classification(
        data_interface, node, visualize=False
    )

    inject_intervals = pd.read_csv(
        inject_intervals_path, index_col=inject_intervals_index_column
    ).astype(int)

    checking_df = dict()
    for run_name, row in node_seu_logs.iterrows():
        register = "x" + str(
            (number_of_registers - 1) - int(row["register"].split("[")[1].strip("]"))
        )
        injection_cycle = int(
            float(row[seu_injection_cycle_column])
        )  # TODO: rounding of half cycle happens here! does it need a change?
        bit_number = int(row[bit_number_column])
        seed = int(row[seed_column].split("\x1b")[0])
        error_class = error_classification.loc[run_name]
        is_silent = error_class == SilentError.name
        try:
            is_sensitive = inject_intervals[register][injection_cycle] != 0
            encoded_cycle = inject_intervals[register][injection_cycle]
        except KeyError:
            cp.print_fail("===== WARNING =====")
            cp.print_fail(f"Run {run_name} is not in encoded_intervals")
            cp.print_fail(f"Register: {register}")
            cp.print_fail(f"Cycle: {injection_cycle}")
            cp.print_fail("")
            continue

        checking_df[run_name] = {
            "register": register,
            "injection_cycle": injection_cycle,
            "bit_number": bit_number,
            "seed": seed,
            "error_class": error_class,
            "is_silent": is_silent,
            "is_sensitive": is_sensitive,
            "encoded_cycle": encoded_cycle,
        }
    checking_df = pd.DataFrame(checking_df).T
    # ==================================================================================

    # ==================================================================================
    # Test if all non_sensitive injections are silent
    # ==================================================================================
    false_negative_check_df = checking_df.copy()
    false_negative_check_df["is_false_negative"] = false_negative_check_df.apply(
        lambda row: not row["is_silent"] and not row["is_sensitive"], axis=1
    )

    cp.print_bold("Non-silent error in non-sensitive injections check:")
    if false_negative_check_df["is_false_negative"].any():
        cp.print_fail("Test failed. Some non-sensitive injections are not silent.")
        print(false_negative_check_df["is_false_negative"].value_counts())
    else:
        cp.print_ok("Test passed. All non-sensitive injections are silent.")
    print("")

    if save_false_negatives:
        false_negative_check_df[false_negative_check_df["is_false_negative"]][
            ["register", "injection_cycle", "seed"]
        ].to_csv("test/false_negatives.csv")

    f1 = checking_df.apply(
        lambda row: not row["is_silent"] and not row["is_sensitive"], axis=1
    )
    f2 = checking_df.apply(
        lambda row: not row["is_silent"] and row["is_sensitive"], axis=1
    )
    f3 = checking_df.apply(
        lambda row: row["is_silent"] and not row["is_sensitive"], axis=1
    )
    f4 = checking_df.apply(lambda row: row["is_silent"] and row["is_sensitive"], axis=1)
    # ==================================================================================

    # ==================================================================================
    # Test if all equivalent injections are of the same error class
    # ==================================================================================
    equivalent_injection_check_df = checking_df.copy()
    equivalent_injection_check_df = equivalent_injection_check_df[
        equivalent_injection_check_df["encoded_cycle"] != 0
    ]

    equivalent_injection_check_df["unique"] = equivalent_injection_check_df.apply(
        lambda row: "Register: "
        + str(row["register"])
        + "\nEncoded cycle: "
        + str(row["encoded_cycle"])
        + "\nBit number: "
        + str(row["bit_number"]),
        axis=1,
    )

    i = 0
    for unique_val, unique in equivalent_injection_check_df.groupby("unique"):
        if unique["error_class"].nunique() == 1:
            continue

        i += 1

        if save_injection_interval_assumption:
            unique[
                [
                    "register",
                    "encoded_cycle",
                    "injection_cycle",
                    "bit_number",
                    "seed",
                    "error_class",
                ]
            ].to_csv(f"test/injection_interval_assumption_{i}.csv")

    cp.print_bold("Equivalent injection check:")
    if i == 0:
        cp.print_ok(
            "Test passed. All equivalent injections are of the same error class."
        )
    else:
        cp.print_fail(
            "Test failed. Some equivalent injections are not of the same error class."
        )

    _ = ""
