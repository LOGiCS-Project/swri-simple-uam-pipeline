from attrs import define, field
from util.config import Config, PathConfig

@define
class SetupConfig():
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html
    """
    example_str : str = "Default Value"
    example_int : int = 12

# Add to the configuration manager
Config.register(
    SetupConfig,
    interpolation_key = "setup",
    conf_file = "setup.conf.yaml",
    conf_deps = [PathConfig],
)
