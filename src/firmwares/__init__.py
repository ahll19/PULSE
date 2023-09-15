from .mappings import MappingMethods

# change the lines below to import your own firmware mappings
# the important thing is important as RunInfo, SeuRunInfo, and InfoMapper
# TODO: make this an option from the analysis call
from .coremark import CoremarkRunInfo as RunInfo
from .coremark import CoremarkSeuRunInfo as SeuRunInfo
from .coremark import CoremarkInfoMapper as InfoMapper
