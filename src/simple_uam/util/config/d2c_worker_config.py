from attrs import define, field
from .path_config import PathConfig
from .manager import Config

@define
class D2CWorkerConfig():
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html
    """
    example_str : str = "Default Value"
    example_int : int = 12

# Add to the configuration manager
Config.register(
    D2CWorkerConfig, # class to be registered

    conf_deps = [PathConfig],
    conf_file = "d2c_worker.conf.yaml",
    interpolation_key = "d2c_worker",
)
