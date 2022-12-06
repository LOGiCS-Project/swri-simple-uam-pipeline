
from parsy import *
from .line_parser import *
from .block_parser import *
from .util import *
from simple_uam.util.logging import get_logger
from attrs import define, field
log = get_logger(__name__)

def header_line():
    """
    This parses lines like:
    ```
    #Metrics
    ```
    """

    return parse_line(wrap_whitespace(string('#Metrics')))

def kv_pair_line():
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

    @generate
    def str_parse_line():
        key = yield test_char(lambda c: not c.isspace(),"not space").at_least(1).concat()
        yield whitespace
        value = yield scientific
        return (key, value)

    return parse_line(wrap_whitespace(str_parse_line))

@generate
def metrics_lines():
    """
    This parses blocks like:
    ```
    #Metrics
    Flight_path            3
    Path_traverse_score_based_on_requirements    0.00000000
    ```
    """

    yield header_line()
    pairs = yield kv_pair_line().at_least(1)
    return {k : v for (k,v) in pairs}

metrics_block = parse_block('metrics_block', metrics_lines)
