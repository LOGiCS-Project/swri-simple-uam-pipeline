
from parsy import *
from .line_parser import *
from .util import *
from simple_uam.util.logging import get_logger
from attrs import define, field
log = get_logger(__name__)

def subhead_line():
    """
    This parses lines like:
    ```
    +----- Motor ----+  +---- Battery ---+
    ```
    """

    def single_subhead(name):

        subhead_prefix = string('+') + string('-').at_least(3).concat()
        subhead_suffix = string('-').at_least(3).concat() + string('+')

        return seq(
            subhead_prefix,
            whitespace,
            string(name),
            whitespace,
            subhead_suffix,
        ).result(name)

    return parse_line(wrap_whitespace(seq(
        single_subhead('Motor'),
        whitespace,
        single_subhead('Battery'),
    ))).result(True)

def header_line():
    """
    This parses lines like:
    ```
    Motor #    omega     omega    Voltage    Thrust    Torque    Power    Current Efficiency Max Powe r  Max Cur  Peak Cur  Cont Cur
    ```
    """

    header_choices = [
        'omega',
        'Voltage',
        'Thrust',
        'Torque',
        'Power',
        'Current',
        'Efficiency',
        'Max Powe r',
        'Max Cur',
        'Peak Cur',
        'Cont Cur',
    ]

    return parse_line(wrap_whitespace(
        string('Motor #') >> whitespace >> string_from(*header_choices).sep_by(whitespace)
    ))

def units_line():
    """
    This parses lines like:
    ```
    (rad/s)    (RPM)    (volts)      (N)       (Nm)   (watts)    (amps)      (%)    (watts)    (amps)    (amps)    (amps)
    ```
    """

    units_choices = [
        '(rad/s)',
        '(RPM)',
        '(volts)',
        '(N)',
        '(Nm)',
        '(watts)',
        '(amps)',
        '(%)',
    ]

    return parse_line(wrap_whitespace(
        string_from(*units_choices).sep_by(whitespace)
    ))


def data_line():
    """
    This parses lines like:
    ```
    Max Volt  2   1790.47  17097.72     22.20     12.05      0.24    530.03     23.88     85.18    532.00     24.00    900.00    450.00
    ```
    """

    max_types = [
        'Volt',
        'Power',
        'Amps',
    ]

    @generate
    def data_str():
        yield string('Max')
        yield whitespace
        max_type = yield string_from(*max_types)
        yield whitespace
        motor_num = yield decimal_digit
        yield whitespace
        data_vals = yield scientific.sep_by(whitespace)
        return dict(
            max=max_type,
            motor=motor_num,
            data=data_vals,
        )

    return parse_line(wrap_whitespace(data_str))

@generate
def motor_power_block():
    """
    This is the parser for blocks like:

    ```
                                                                                                 +----- Motor ----+  +---- Battery ---+
        Motor #    omega     omega    Voltage    Thrust    Torque    Power    Current Efficiency Max Powe r  Max Cur  Peak Cur  Cont Cur
                  (rad/s)    (RPM)    (volts)      (N)       (Nm)   (watts)    (amps)      (%)    (watts)    (amps)    (amps)    (amps)
    Max Volt  1   1790.47  17097.72     22.20     12.05      0.24    530.03     23.88     85.18    532.00     24.00    900.00    450.00
    Max Volt  2   1790.47  17097.72     22.20     12.05      0.24    530.03     23.88     85.18    532.00     24.00    900.00    450.00
    ...
    ```
    """
    yield subhead_line()
    headers = yield header_line()
    units = yield units_line()
    data = yield data_line().many()

    output = list()

    for row in data():

        formatted = dict(
            max=row['max'],
            motor=row['motor'],
        )

        for ind, val in enumerate(row['data']):
            entry_name = headers[ind]
            entry_units = units[ind].strip('()')
            entry_value = val

            formatted[entry_name] = dict(
                units=entry_units,
                value=entry_value,
            )

        output.append(formatted)

    return output
