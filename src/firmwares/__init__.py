from .mappings import MappingMethods

# change the lines below to import your own firmware mappings
# the important thing is important as RunInfo, SeuRunInfo, and InfoMapper
# TODO: make this an option from the analysis call
from .coremark_ibex_hwsec import RunInfo 
from .coremark_ibex_hwsec import SeuRunInfo 
from .coremark_ibex_hwsec import InfoMapper 
