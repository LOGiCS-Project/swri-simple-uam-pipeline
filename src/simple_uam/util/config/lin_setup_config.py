from attrs import define, field
from .manager import Config
from typing import List

@define
class LinSetupConfig():
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html
    """

    global_dep_packages : List[str] = [
        'checksum',
        'wget',
        '7zip',
    ]
    """
    Packages that are needed for all linux nodes, please don't remove any
    from this default set.
    """

# Add to the configuration manager
Config.register(
    LinSetupConfig,
    interpolation_key = "lin_setup",
    conf_file = "lin_setup.conf.yaml",
    conf_deps = [],
)
