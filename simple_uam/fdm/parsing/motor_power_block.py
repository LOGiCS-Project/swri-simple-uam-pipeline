
from parsy import *
from .line_parser import *
from .block_parser import *
from .util import *
from simple_uam.util.logging import get_logger
from attrs import define, field
log = get_logger(__name__)

dashes = string('-').at_least(2)

subhead_line_parser = parse_strip_line(
    format_parser(
        '+${d1} Motor ${d2}+  +${d3} Battery ${d4}+',
        d1 = dashes,
        d2 = dashes,
        d3 = dashes,
        d4 = dashes,
    ).result(None)
)
"""
This parses lines like:
```
+----- Motor ----+  +---- Battery ---+
```
"""

header_col_choices = {
    'omega': 'omega',
    'Voltage': 'voltage',
    'Thrust': 'thrust',
    'Torque': 'torque',
    'Power': 'power',
    'Current': 'current',
    'Efficiency': 'efficiency',
    'Max Power': 'max_power',
    'Max Cur': 'max_current',
    'Peak Cur': 'peak_current',
    'Cont Cur': 'continuous_current',
}

header_col_str_parser = alt(
    *[string(col).result(var) for col,var in header_col_choices.items()]
)

@generate
def header_str_parser():
    """
    This parses lines like:
    ```
    Motor #    omega     omega    Voltage    Thrust    Torque    Power    Current Efficiency Max Powe r  Max Cur  Peak Cur  Cont Cur
    ```
    """

    return string('Motor #') >> header_col_str_parser.sep_by(whitespace)

header_line_parser = parse_strip_line(header_str_parser)

units_str_parser = in_parens.sep_by(whitespace)
"""
This parses lines like:
```
(rad/s)    (RPM)    (volts)      (N)       (Nm)   (watts)    (amps)      (%)    (watts)    (amps)    (amps)    (amps)
```
"""

units_line_parser = parse_strip_line(units_str_parser)

motor_states = {
    'Volt': 'voltage',
    'Power': 'power',
    'Amps': 'current',
}

motor_state_str_parser = string('Max') >> whitespace >> alt(
    *[string(k).result(f'maximum_{v}') for k, v in motor_states.items()]
)

def data_line_parser(col_headers, col_units):
    """
    This parses lines like:
    ```
    Max Volt  2   1790.47  17097.72     22.20     12.05      0.24    530.03     23.88     85.18    532.00     24.00    900.00    450.00
    ```
    """

    @generate
    def data_str_parser():

        row = dict()

        row['motor_state'] = yield motor_state_str_parser << whitespace
        row['motor_number'] = yield int_p << whitespace

        data_points = yield scientific.sep_by(whitespace)

        for (i, val) in enumerate(data_points):
            row[col_headers[i]] = with_units(val, col_units[i])

        return row

    return parse_strip_line(data_str_parser)

@generate
def motor_power_lines():
    """
    This is the line parser for blocks like:

    ```
                                                                                                 +----- Motor ----+  +---- Battery ---+
        Motor #    omega     omega    Voltage    Thrust    Torque    Power    Current Efficiency Max Powe r  Max Cur  Peak Cur  Cont Cur
                  (rad/s)    (RPM)    (volts)      (N)       (Nm)   (watts)    (amps)      (%)    (watts)    (amps)    (amps)    (amps)
    Max Volt  1   1790.47  17097.72     22.20     12.05      0.24    530.03     23.88     85.18    532.00     24.00    900.00    450.00
    Max Volt  2   1790.47  17097.72     22.20     12.05      0.24    530.03     23.88     85.18    532.00     24.00    900.00    450.00
    ...
    ```
    """
    yield subhead_line_parser

    col_headers = yield header_line_parser
    col_units = yield units_line_parser
    rows = yield data_line_parser(col_headers, col_units).many()

    return rows

motor_power_block = parse_block('motor_power_block', motor_power_lines)
