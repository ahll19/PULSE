- [PULSE](#pulse)
  - [Prerequisites](#prerequisites)
    - [Python](#python)
    - [Data](#data)
  - [Structure](#structure)
      - [Run info](#run-info)
  - [Quick start](#quick-start)

# PULSE
PULSE (*Python-based seU Log Statistics and Evaluation*) is a tool for analyzing the stdout logs of fault injection simulations. 

![Temporary image](img/ai.jpg)

## Prerequisites
### Python
In order to use PULSE you must set up the Python environment on your machine by running
```
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
How to install the `venv` package to your distributions global Python environment depends on your distribution.

### Data
You also need to have data from several SEU runs, in the following format
```
data
├── golden_coremark_stdout.log
├── golden_trace.log
├── reg_tree.txt
├── seu_2023-09-11_16-45-09.361189
│   └── log.txt
├── seu_2023-09-11_16-45-09.361236
│   └── log.txt
.
.
.
```
The `log.txt` files are the stdout logs of your SEU runs. <br>
The `golden_trace.log` file, which contains the core trace, is not strictly necessary for the tool, as of November $1^{\text{st}}$ 2023. <br>
The `golden_coremark_stdout.log` file is the file containing the stdout log of the golden run. <br>
The `reg_tree.txt` file is a list of all registers that are available for injection to the simulator.

## Structure
Will be written more in depth once Anders finishes his worksheet on PULSE.

The general structure of the `src` directory is shown below.
```
src
├── analysis
│   ├── base_tools.py
│   ├── ibex_coremark_tools.py
│   ├── ibex_hwsec_coremark_tools.py
│   └── structures
│       ├── error_definitions.py
│       ├── error_probability.py
├── colorprint.py
├── data_interface.py
├── data_parser.py
└── run_info
    ├── example_run_info
    │   ├── ...
    ├── ibex_coremark.ini
    ├── ibex_hwsec_coremark.ini
    ├── run_info.py
    └── sections.py
```

**blah blah blah**

#### Run info
The file `ibex_coremark.ini` file is the configuration of a given type of run on some given hardware (in this case the Ibex SoC, with Coremark running). This file should function as a template for other configurations. There are 5 sections in the config:
- `DATA`
  - Every field in this section MUST be filled, and point to a valid directory / file (except timeout, which is only used if you want to only read logs for some max amount of time).
- `DEBUG`
  - Every field in this section MUST be filled, and be either 0 or 1.
  - Debugging for different parts of the parsing can be turned on. If you are brave enough you can also add debugging options rather easily to other parts of the code
- `COMPARISON_DATA`
  - This section is used to define what data should be pulled from the logs.
  - The data specified in this section must be present in a full SEU run (where the logs aren't cut off early), and the golden run.
  - If a line in this section is e.g. `matrix_crc=[0]crcmatrix` the tool will create a variable in python called `matrix_crc` (on the run_info object). The data-parser will then find the first line in the log matching `[0]crcmatrix`. The parser will split this line by the string `[0]crcmatrix`, and take the second entry (if the string `[0]crcmatrix` appears multiple times only this second entry in the split line will be saved).
  - This parsed value will then be stored.
- `SEU_METADATA`
  - This section is for defining data unique to the SEU runs, which we want to save.
  - The parsing and saving is done by the same method as in `COMPARISON_DATA`
  - There MUST be an entry in this section called `register` which defines where we inject on the chip. If this line is not defined the tool will not run.
- `OPTIONAL_DATA`
  - This section is for data we want from the SEU runs, where it will not always be present, or perhaps it will be present multiple times.

The `sections.py` file defines behavior for each of the sections defined above. The `run_info.py` collects these sections into an object which can be used in the analysis tools, and by the user to check run configurations. <br>
The `RunInfo` object should only really be interacted with for debugging purposes (making sure the `register` match string is correct for example).

## Quick start
In order to see how to use the tools, consult the `examples.ipynb` in the source directory of the repository.