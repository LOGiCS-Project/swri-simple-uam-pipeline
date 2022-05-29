from attrs import define, field
from util.config import Config, PathConfig

@define
class UAMWorkerConfig():
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html
    """
    example_str : str = "Default Value"
    example_int : int = 12

# Add to the configuration manager
Config.register(
    UAMWorkerConfig, # class to be registered

    conf_deps = [PathConfig],
    # Config classes this can interpolate with.
    # e.g. If `PathConfig` is in `conf_deps` this config file (and the defaults)
    #      can use "${path:data_dir}/foo/bar.txt" and have it resolve correctly.

    conf_file = "uam_worker.conf.yaml",
    # The file that will be loaded to fill out this config class.
    # i.e. If you write: `example_int: 32` to "${path:config_dir}/uam_worker.conf.yaml"
    #      then `Config[UAMWorkerConfig].example_int == 32`.

    interpolation_key = "uam_worker",
    # Key used by other config classes to access variables in this class.
    # e.g. If another config class registers `UAMWorkerConfig` in its
    #      `conf_deps`, it can use "${uam_worker:example_str}"
    #      in its own definitions.
)