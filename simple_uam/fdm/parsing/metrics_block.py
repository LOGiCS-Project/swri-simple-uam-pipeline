
from parsy import *
from .line_parser import *
from .block_parser import *
from .util import *
from simple_uam.util.logging import get_logger
from attrs import define, field
log = get_logger(__name__)


header_line_parser = parse_strip_line(string('#Metrics'))
"""
This parses lines line:
```
#Metrics
```
"""

metrics_known_units = {
    'Flight_distance': 'm',
    'Time_to_traverse_path': 's',
    'Average_speed_to_traverse_path': 'm/s',
    'Maximimum_error_distance_during_flight': 'm',
    'Velocity_at_time_of_maximum_distance_error': 'm/s',
    'Spatial_average_distance_error': 'm',
    'Maximum_ground_impact_speed': 'm/s',
}

@generate
def key_str_parser():

    key = yield not_spaces_or("()")
    unit = yield in_parens.optional(None)
    key = key.strip('_')

    if key in metrics_known_units and unit == None:
        unit = metrics_known_units[key]

    return (to_undercase(key), unit)

@generate
def kv_pair_str_parser():
    """
    This parses lines line:
    ```
    Distance_at_Max_Speed_(m)    6262.88965
    Power_at_Max_Speed_(W)    627.368103
    Motor_amps_to_max_amps_ratio_at_Max_Speed   0.645317852
    Motor_power_to_max_power_ratio_at_Max_Speed   0.646288216
    Battery_amps_to_max_amps_ratio_at_Max_Speed    7.97076151E-02
    ```
    """

    (key, unit) = yield key_str_parser
    yield whitespace
    values = yield alt(scientific, not_spaces).sep_by(whitespace,min=1)

    # log.debug(
    #     "parsing metrics line",
    #     key=key,
    #     unit=unit,
    #     values=values,
    # )

    if len(values) == 1:
        return { key : with_units(values[0], unit) }
    else:
        return { key : [with_units(v, unit) for v in values] }

requested_trim_str_parser = format_parser(
    'Requested trim condition not found'
).result({'trim_condition_not_found': True})

kv_pair_line_parser = parse_strip_line(
    alt(kv_pair_str_parser, requested_trim_str_parser)
)

metrics_lines_parser = (
    header_line_parser >> union_many(kv_pair_line_parser, min=1)
)
"""
This parses blocks like:
```
#Metrics
Flight_path            3
Path_traverse_score_based_on_requirements    0.00000000
```
"""

metrics_block = parse_block('metrics_block', metrics_lines_parser)
