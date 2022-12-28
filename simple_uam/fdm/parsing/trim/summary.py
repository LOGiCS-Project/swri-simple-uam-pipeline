from parsy import *
from copy import deepcopy, copy
from ..line_parser import *
from ..block_parser import *
from ..util import *
from .shared import *
from simple_uam.util.logging import get_logger
log = get_logger(__name__)


trim_state_count_str_parser = format_parser(
    "Trim states:  ${minpack} found by MINPACK, " \
    "${simplex} found by nonlinear simplex.",
    minpack=int_p,
    simplex=int_p,
).dtag('trim_state_count')
"""
parses lines like:
```
Trim states:  0 found by MINPACK, 14 found by nonlinear simplex.  SIM/MIN means simplex found a solution and minpack successfully polished it.
```
"""

trim_state_count_minpack_suffix_str_parser = format_parser(
    "$s?SIM/MIN means simplex found a solution and minpack "\
    "successfully polished it."
) # gets appended to trim state count line above if minpack_trim



control_state_count_line_parser = parse_strip_line(
    format_parser(
        "Control states found by RICPACK solving the "\
        "Algebraic Riccati Equation (ARE): ${via_are}",
        via_are=int_p,
    )
).dtag('control_state_count')
"""
parses lines like:
```
Control states found by RICPACK solving the Algebraic Riccati Equation (ARE): 14
```
"""

summary_prefix_header_lines = static_lines(
    """
    Summary of no-warning steady state trims (thrust, lift, and drag are vector magnitudes).  Frac amp is the ratio of the current in the
    motor divided by the maximum allowed current, then the maximum is taken over all the motors.  Frac pow is the same thing for motor power.
    Frac current is the battery current divided by maximum allowable battery current, taken over all the batteries.
    These Frac values should be less than 1.  Max uc is the max control variable uc (or throttle).
    """
)

summary_turning_radius_line_parser = parse_strip_line(
    format_parser(
        'Turning radius    ${turning_radius} m '\
        '(positive means clockwise looking down)',
        turning_radius=scientific.with_units('m'),
    )
)

@generate
def table_header_str_parser():
    """
    Parses lines like:
    ```
    Lateral speed  Distance  Flight time  Pitch angle  Max uc    Thrust      Lift       Drag    Current  Total power Frac amp  Frac pow  Frac current
    ```
    """

    header_cols = {
        'Lateral speed': 'lateral_speed',
        'Tangent speed': 'tangent_speed',
        'Distance': 'distance',
        'Flight time': 'flight_time',
        'Pitch angle': 'pitch_angle',
        'Roll angle': 'roll_angle',
        'Max uc': 'max_uc',
        'Thrust': 'thrust',
        'Lift': 'lift',
        'Drag': 'drag',
        'Current': 'current',
        'Total power': 'total_power',
        'Frac amp': 'motor_current_max',
        'Frac pow': 'motor_power_max',
        'Frac current': 'battery_current_max',
    }

    col_parsers = [string(k).result(v) for k, v in header_cols.items()]

    cols = yield alt(*col_parsers).sep_by(whitespace)

    return cols

table_header_line_parser = parse_strip_line(table_header_str_parser)

@generate
def table_units_str_parser():

    units = yield in_parens.sep_by(whitespace)

    return [u if u != '-' else None for u in units]

table_units_line_parser = parse_strip_line(table_units_str_parser)

def not_iwarn_line_parser(base_cols, base_units, extra_cols):
    """
    Parses lines like:
    ```
    0.00        0.00      498.28       -0.00       0.85      20.79       0.00       0.00      34.68     589.71     0.586     0.587     0.077     SIMPLEX  ARE
    ```
    """

    @generate
    def not_iwarn_str_parser():

        row = dict()

        num_base = len(base_cols)
        values = yield scientific.sep_by(whitespace, min=num_base, max=num_base)
        for (i, val) in enumerate(values):
            row[base_cols[i]] = with_units(val,base_units[i])

        for (k,parser) in extra_cols:
            row[k] = yield whitespace.optional() >> parser

        return row

    return parse_strip_line(not_iwarn_str_parser)

def iwarn_line_parser(base_cols, base_units):
    """
    Parses lines like:
    ```
    26.00                                                                                                                                 2.9866803E+00    1.5586600E+01
    ```
    """

    @generate
    def iwarn_str_parser():

        row = dict()

        num_cols = len(base_cols)
        values = yield scientific.sep_by(whitespace, min=num_cols, max=num_cols)

        for (i, val) in enumerate(values):
            row[base_cols[i]] = with_units(val, base_units[i])

        return row

    return parse_strip_line(iwarn_str_parser)

@generate
def summary_table_lines_parser():
    """
    parses lines like:
    ```
    Lateral speed  Distance  Flight time  Pitch angle  Max uc    Thrust      Lift       Drag    Current  Total power Frac amp  Frac pow  Frac current
        (m/s)        (m)         (s)        (deg)        (-)       (N)        (N)        (N)       (amp)     (watt)      (-)       (-)       (-)
         0.00        0.00      498.28       -0.00       0.85      20.79       0.00       0.00      34.68     589.71     0.586     0.587     0.077     SIMPLEX  ARE
         1.00      498.25      498.25       -0.04       0.85      20.79       0.00       0.01      34.68     589.82     0.586     0.587     0.077     SIMPLEX  ARE
         2.00      996.26      498.13       -0.16       0.85      20.79       0.00       0.06      34.69     590.15     0.587     0.588     0.077     SIMPLEX  ARE
         3.00     1493.64      497.88       -0.35       0.85      20.79       0.00       0.13      34.71     590.78     0.589     0.590     0.077     SIMPLEX  ARE
         4.00     1989.86      497.47       -0.63       0.85      20.79       0.00       0.23      34.74     591.76     0.591     0.592     0.077     SIMPLEX  ARE
         5.00     2484.20      496.84       -0.98       0.85      20.78       0.00       0.36      34.78     593.16     0.594     0.595     0.077     SIMPLEX  ARE
         6.00     2976.08      496.01       -1.41       0.85      20.78       0.00       0.51      34.84     594.99     0.598     0.599     0.077     SIMPLEX  ARE
         7.00     3464.47      494.92       -1.93       0.85      20.78       0.00       0.70      34.91     597.35     0.602     0.603     0.078     SIMPLEX  ARE
         8.00     3948.50      493.56       -2.51       0.86      20.77       0.00       0.91      35.01     600.29     0.607     0.608     0.078     SIMPLEX  ARE
         9.00     4427.50      491.94       -3.18       0.86      20.76       0.00       1.15      35.13     603.85     0.613     0.614     0.078     SIMPLEX  ARE
        10.00     4898.74      489.87       -3.92       0.86      20.74       0.00       1.42      35.27     608.39     0.620     0.621     0.078     SIMPLEX  ARE
        11.00     5360.82      487.35       -4.73       0.87      20.73       0.00       1.71      35.46     613.96     0.628     0.629     0.079     SIMPLEX  ARE
        12.00     5814.20      484.52       -5.62       0.87      20.70       0.00       2.03      35.66     620.41     0.637     0.637     0.079     SIMPLEX  ARE
        13.00     6262.89      481.76       -6.57       0.87      20.68       0.00       2.38      35.87     627.37     0.645     0.646     0.080     SIMPLEX  ARE
        14.00                                                                                                                                 4.0310717E-02    2.3213900E-03
        15.00                                                                                                                                 3.4641713E-01    1.3576317E-01
        16.00                                                                                                                                 6.8861928E-01    5.3964044E-01
        17.00                                                                                                                                 1.0461138E+00    1.2480830E+00
        18.00                                                                                                                                 1.3942656E+00    2.2675933E+00
        19.00                                                                                                                                 1.7182289E+00    3.5365724E+00
        20.00                                                                                                                                 2.0251802E+00    6.6606368E+00
        21.00                                                                                                                                 2.1998314E+00    6.8163863E+00
        22.00                                                                                                                                 2.4633151E+00    1.1415318E+01
        23.00                                                                                                                                 2.6976386E+00    1.0421751E+01
        24.00                                                                                                                                 2.8086265E+00    1.2191346E+01
        25.00                                                                                                                                 2.9257389E+00    1.3949369E+01
        26.00                                                                                                                                 2.9866803E+00    1.5586600E+01
        27.00                                                                                                                                 2.9921631E+00    1.7959181E+01
        28.00                                                                                                                                 3.0933256E+00    1.8389571E+01
        29.00                                                                                                                                 3.1720112E+00    2.0266695E+01
        30.00                                                                                                                                 5.6547596E+00    4.6982798E+01
        31.00                                                                                                                                 3.3862387E+00    2.2555089E+01
        32.00                                                                                                                                -1.0220122E+01    1.2876265E+02
        33.00                                                                                                                                -1.0162586E+01    2.1048562E+02
        34.00                                                                                                                                -1.0423856E+01    1.4633742E+02
        35.00                                                                                                                                 8.3875290E+00    1.0999795E+02
        36.00                                                                                                                                -1.0484086E+01    2.3840990E+02
        37.00                                                                                                                                 6.0145490E+00    4.7518039E+01
        38.00                                                                                                                                 7.5807559E+00    8.0933911E+01
        39.00                                                                                                                                -1.0894108E+01    2.1018705E+02
        40.00                                                                                                                                -1.1014164E+01    2.2674158E+02
        41.00                                                                                                                                -1.1111891E+01    2.4494773E+02
        42.00                                                                                                                                -1.1210123E+01    2.6472557E+02
        43.00                                                                                                                                -1.1653314E+01    2.8616786E+02
        44.00                                                                                                                                -1.2449256E+01    3.0936019E+02
        45.00                                                                                                                                -1.3148248E+01    3.3323925E+02
        46.00                                                                                                                                -1.4072225E+01    3.5915205E+02
        47.00                                                                                                                                -1.4916766E+01    3.8778047E+02
        48.00                                                                                                                                -1.5731719E+01    4.1808914E+02
        49.00                                                                                                                                -1.6566553E+01    4.4984032E+02
        50.00                                                                                                                                -1.7507331E+01    4.8443622E+02
    ```
    """

    no_warn_cols  = yield table_header_line_parser
    no_warn_units = yield table_units_line_parser
    extra_cols = [
        ('solver',csolve_str_parser),
        ('are',are_str_parser),
    ]

    speed_col = None
    if 'tangent_speed' in no_warn_cols:
        speed_col = 'tangent_speed'
    elif 'lateral_speed' in no_warn_cols:
        speed_col = 'lateral_speed'

    speed_unit = no_warn_units[no_warn_cols.index(speed_col)]

    warn_cols = [speed_col, 'trim_max_xd', 'trim_fd_cost']
    warn_units = [speed_unit, None, None]

    rows = yield tag_alt(
        'warn',
        true=iwarn_line_parser(warn_cols, warn_units),
        false=not_iwarn_line_parser(no_warn_cols, no_warn_units, extra_cols),
    ).at_least(50)

    return {'summary': rows}
