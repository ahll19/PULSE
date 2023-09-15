from time import time as get_curr_time


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


class ColorPrinter:
    @staticmethod
    def print_header(text: str, end="\n") -> None:
        print(f"{bcolors.HEADER}{text}{bcolors.ENDC}", end=end)

    @staticmethod
    def print_okblue(text: str, end="\n") -> None:
        print(f"{bcolors.OKBLUE}{text}{bcolors.ENDC}", end=end)

    @staticmethod
    def print_okcyan(text: str, end="\n") -> None:
        print(f"{bcolors.OKCYAN}{text}{bcolors.ENDC}", end=end)

    @staticmethod
    def print_okgreen(text: str, end="\n") -> None:
        print(f"{bcolors.OKGREEN}{text}{bcolors.ENDC}", end=end)

    @staticmethod
    def print_warning(text: str, end="\n") -> None:
        print(f"{bcolors.WARNING}{text}{bcolors.ENDC}", end=end)

    @staticmethod
    def print_fail(text: str, end="\n") -> None:
        print(f"{bcolors.FAIL}{text}{bcolors.ENDC}", end=end)

    @staticmethod
    def print_bold(text: str, end="\n") -> None:
        print(f"{bcolors.BOLD}{text}{bcolors.ENDC}", end=end)

    @staticmethod
    def print_bold_okblue(text: str, end="\n") -> None:
        print(f"{bcolors.BOLD}{bcolors.OKBLUE}{text}{bcolors.ENDC}", end=end)

    @staticmethod
    def print_bold_okcyan(text: str, end="\n") -> None:
        print(f"{bcolors.BOLD}{bcolors.OKCYAN}{text}{bcolors.ENDC}", end=end)

    @staticmethod
    def print_bold_okgreen(text: str, end="\n") -> None:
        print(f"{bcolors.BOLD}{bcolors.OKGREEN}{text}{bcolors.ENDC}", end=end)

    @staticmethod
    def print_bold_warning(text: str, end="\n") -> None:
        print(f"{bcolors.BOLD}{bcolors.WARNING}{text}{bcolors.ENDC}", end=end)

    @staticmethod
    def print_bold_fail(text: str, end="\n") -> None:
        print(f"{bcolors.BOLD}{bcolors.FAIL}{text}{bcolors.ENDC}", end=end)

    @staticmethod
    def print_func_time(func):
        def wrapper(*args, **kwargs):
            ColorPrinter.print_bold_okgreen(
                f"Running function {func.__name__}. ", end=""
            )
            start_time = get_curr_time()
            result = func(*args, **kwargs)
            end_time = get_curr_time()
            ColorPrinter.print_bold_okgreen(
                f"Took: {end_time - start_time:.2f} seconds"
            )
            return result

        return wrapper


if __name__ == "__main__":
    # Test the ColorPrinter class
    ColorPrinter.print_header("This is a header")
    ColorPrinter.print_okblue("This is ok blue")
    ColorPrinter.print_okcyan("This is ok cyan")
    ColorPrinter.print_okgreen("This is ok green")
    ColorPrinter.print_warning("This is a warning")
    ColorPrinter.print_fail("This is a fail")
    ColorPrinter.print_bold("This is bold")
    ColorPrinter.print_bold_okblue("This is bold and ok blue")
    ColorPrinter.print_bold_okcyan("This is bold and ok cyan")
    ColorPrinter.print_bold_okgreen("This is bold and ok green")
    ColorPrinter.print_bold_warning("This is bold and a warning")
    ColorPrinter.print_bold_fail("This is bold and a fail")
