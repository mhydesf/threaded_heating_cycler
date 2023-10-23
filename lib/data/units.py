from collections import namedtuple


LoopDataPoint = namedtuple(
    "LoopDataPoint",
    [
        "therm_L_C",
        "therm_R_C",
        "duty_cycle",
    ]
)

DataPoint = namedtuple(
    "DataPoint",
    [
        "timestamp",
        "therm_L_C",
        "therm_R_C",
        "duty_cycle",
        "cycle",
    ]
)

CycleDataPoint = namedtuple(
    "CycleDataPoint",
    [
        "max_temp_C",
        "min_temp_C",
        "ss_temp_C",
        "ss_pwm",
        "cycle",
    ]
)

