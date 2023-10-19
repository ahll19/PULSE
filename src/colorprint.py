from time import time as get_curr_time


class bcolors:
    HEADER = "\033[95m"
    OK = "\033[92m"
    DEBUG = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


class ColorPrinter:
    # Special ==========================================================================
    @staticmethod
    def print_header(text: str, end="\n") -> None:
        print(f"{bcolors.HEADER}{text}{bcolors.ENDC}", end=end)

    @staticmethod
    def print_bold(text: str, end="\n") -> None:
        print(f"{bcolors.BOLD}{text}{bcolors.ENDC}", end=end)

    # Ok ===============================================================================
    @staticmethod
    def print_ok(text: str, end="\n") -> None:
        print(f"{bcolors.OK}{text}{bcolors.ENDC}", end=end)

    @staticmethod
    def print_bold_ok(text: str, end="\n") -> None:
        print(f"{bcolors.BOLD}{bcolors.OK}{text}{bcolors.ENDC}", end=end)

    # Warning ==========================================================================
    @staticmethod
    def print_debug(text: str, end="\n") -> None:
        print(f"{bcolors.DEBUG}{text}{bcolors.ENDC}", end=end)

    @staticmethod
    def print_bold_debug(text: str, end="\n") -> None:
        print(f"{bcolors.BOLD}{bcolors.DEBUG}{text}{bcolors.ENDC}", end=end)

    # Fail =============================================================================
    @staticmethod
    def print_bold_fail(text: str, end="\n") -> None:
        print(f"{bcolors.BOLD}{bcolors.FAIL}{text}{bcolors.ENDC}", end=end)

    @staticmethod
    def print_fail(text: str, end="\n") -> None:
        print(f"{bcolors.FAIL}{text}{bcolors.ENDC}", end=end)

    # Other ============================================================================
    @staticmethod
    def print_func_time(func):
        def wrapper(*args, **kwargs):
            ColorPrinter.print_bold_ok(f"Running function {func.__name__}. ", end="")
            start_time = get_curr_time()
            result = func(*args, **kwargs)
            end_time = get_curr_time()
            ColorPrinter.print_bold_ok(f"Took: {end_time - start_time:.2f} seconds")
            return result

        return wrapper


if __name__ == "__main__":
    # test every function
    ColorPrinter.print_header("Header")
    ColorPrinter.print_bold("Bold")
    ColorPrinter.print_ok("Ok")
    ColorPrinter.print_bold_ok("Bold Ok")
    ColorPrinter.print_debug("Warning")
    ColorPrinter.print_bold_debug("Bold Warning")
    ColorPrinter.print_fail("Fail")
    ColorPrinter.print_bold_fail("Bold Fail")
