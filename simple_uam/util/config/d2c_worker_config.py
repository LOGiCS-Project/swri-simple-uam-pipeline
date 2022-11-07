from attrs import define, field
from .path_config import PathConfig
from .craidl_config import CraidlConfig
from .d2c_workspace_config import D2CWorkspaceConfig
from .service_config import ServiceConfig
from .manager import Config
from omegaconf import SI
from typing import Optional

@define
class D2CWorkerConfig():
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html
    """

    max_workspaces : int = 1
    """
    See workspaces config for meaning.
    """

    max_processes : int = 4
    """
    Max number of forked processes on a worker node. This is higher than the
    number of workspaces by default because the FDM operations can handle more
    parallel operations.
    """

    max_threads : int =  1
    """
    Max number of threads per process.
    Default is 1.
    """

    shutdown_timeout : int = 600000
    """
    Timeout for worker shutdown in milliseconds.
    """

    skip_logging : bool = False
    """
    Do we keep dramatiq specific logs? This doesn't affect structlog logs.
    """

    service : ServiceConfig = field(
        default = ServiceConfig(
            stdout_file = SI("${path:log_directory}/d2c_worker/stdout.log"),
            stderr_file = SI("${path:log_directory}/d2c_worker/stderr.log"),
        )
    )
    """
    Settings for running the worker node service.
    """

# Add to the configuration manager
Config.register(
    D2CWorkerConfig, # class to be registered
    conf_deps = [PathConfig, CraidlConfig, D2CWorkspaceConfig],
    conf_file = "d2c_worker.conf.yaml",
    interpolation_key = "d2c_worker",
)
