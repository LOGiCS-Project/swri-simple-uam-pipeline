from attrs import define, field
from .path_config import PathConfig
from .craidl_config import CraidlConfig
from .d2c_workspace_config import D2CWorkspaceConfig
from .service_config import ServiceConfig
from .manager import Config
from omegaconf import SI
from typing import Optional

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
class BrokerConfig():
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html
    """

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

    backend : BackendConfig = BackendConfig()
    """
    Configuration options for a result backend. Needed if you want to get
    return values for remote calls directly.
    """

# Add to the configuration manager
Config.register(
    BrokerConfig, # class to be registered
    conf_deps = [PathConfig],
    conf_file = "broker.conf.yaml",
    interpolation_key = "broker",
)
