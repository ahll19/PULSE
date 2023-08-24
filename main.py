import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from subprocess import call


# Global Path Variables
vcd_file_paths = ["/tools/vcd-diff/vcd_files/" + str(i) + ".vcd" for i in range(1, 10)]
compress_binary_path = "/tools/vcd-diff/compress"
decompress_binary_path = "/tools/vcd-diff/decompress"
vcddiff_binary_path = "/tools/vcdiff/vcddiff"


if __name__ == "__main__":
    pass
