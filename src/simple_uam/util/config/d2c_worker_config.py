from attrs import define, field
from .path_config import PathConfig
from .craidl_config import CraidlConfig
from .d2c_workspace_config import D2CWorkspaceConfig
from .manager import Config
from omegaconf import SI
from typing import Optional

@define
class BrokerConfig():

    protocol : str = 'amqp'
    """
    The broker protocol, must be either 'amqp' (for rabbitmq) or 'redis'
    (for redis).
    """

    host : str = "127.0.0.1"
    """
    The broker host.
    """

    port : int = 5672
    """
    The broker's port.
    """

    db : str = ""
    """
    The database (on redis) or virtualhost (on rabbit mq).
    """

    url : str = '${.protocol}://${.host}:${.port}${.db}'
    """
    The url to connect to for the broker.
    Note that this supersedes all the finer grade connection parameters if
    provided.
    """

@define
class BackendConfig():

    enabled : bool = False
    """
    Is the result backend enabled at all?
    """

    protocol : str = 'redis'
    """
    The result backend protocol only redis is supported for now
    """

    host : str = "127.0.0.1"
    """
    The backend host.
    """

    port : int = 6379
    """
    The broker's port.
    """

    db : str = "0"
    """
    The database (on redis).
    """

    url : str = '${.protocol}://${.host}:${.port}/${.db}'
    """
    The url to connect to for the backend.
    Note that this supersedes all the finer grade connection parameters if
    provided.
    """

@define
class D2CWorkerConfig():
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html
    """

    broker : BrokerConfig = BrokerConfig()
    """
    Configuration options for *connecting to* a broker.
    This applies to both workers and clients.
    """

    backend : BackendConfig = BackendConfig()
    """
    Configuration options for a result backend. Needed if you want to get
    return values for remote calls directly.
    """

    max_processes : int = SI("${d2c_workspace:max_workspaces}")
    """
    Max number of forked processes on a worker node.
    Default is the number of workspaces on the machine.
    """

    max_threads : int = 1
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

# Add to the configuration manager
Config.register(
    D2CWorkerConfig, # class to be registered
    conf_deps = [PathConfig, CraidlConfig, D2CWorkspaceConfig],
    conf_file = "d2c_worker.conf.yaml",
    interpolation_key = "d2c_worker",
)
