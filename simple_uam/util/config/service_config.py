from attrs import define, field
from typing import List, Dict, Optional
from pathlib import Path

@define
class ServiceConfig():
    """
    Dataclass for options concerning how to run a server service.
    """

    priority : str = field(
        default='NORMAL',
        kw_only=True,
    )
    """
    Service run priority, options are: 'REALTIME', 'HIGH', 'ABOVE_NORMAL',
    'NORMAL', 'BELOW_NORMAL', and 'IDLE'.
    """

    exit_action : str = field(
        default='Restart',
        kw_only=True,
    )
    """
    The action to perform if the service exits.
    Options are 'Restart', 'Ignore', and 'Exit'.
    """

    restart_throttle : int = field(
        default=5000,
        kw_only=True,
    )
    """
    Delay restart if app runs for less than given time, in ms.
    """

    restart_delay : int = field(
        default=1000,
        kw_only=True,
    )
    """
    The wait between restarts if the service exits.
    """

    redirect_io : bool = field(
        default=False,
        kw_only=True,
    )
    """
    Redirect IO to files.
    """

    stdout_file : str = field(
    )
    """
    File to redirect stdout to if log redirection is enabled.
    """

    stderr_file : str = field(
    )
    """
    File to redirect stderr to if log redirection is enabled.
    """

    rotate_io : bool = field(
        default=True,
        kw_only=True,
    )
    """
    Rotate out large or old io redirection files.
    """

    # env_vars : Dict[str,str] = field(
    #     factory=dict,
    #     kw_only=True,
    # )
    # """
    # Environment vars to set while running the service as dict from var name to
    # var value.
    # """

    auto_start : bool = field(
        default=False,
        kw_only=True,
    )
    """
    Should this service automatically start on boot?
    """

    console : bool = field(
        default=True,
    )
    """
    Do we run this app in a visible console.
    """

    interactive : bool = field(
        default=False,
    )
    """
    Is this a standalone service or one which can interact the desktop?
    """

    account : str = field(
        default="LocalSystem",
    )
    """
    The user account to run the service with.
    See [here](https://nssm.cc/commands) under "Native parameters" and
    "ObjectName" for more info.
    """

    password : Optional[str] = field(
        default=None,
    )
    """
    The password to the user account that runs this service.
    None means no password is given, empty string is empty string.
    """
