from attrs import define, field
from .manager import Config
from typing import List

@define
class WindowsSetupConfig():
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html
    """

    global_dep_packages : List[str] = [
        # 'sed',
        # 'openjdk11',
        # 'openmodelica',
        # 'putty',
        'checksum',
        'wget',
        '7zip',
        # 'git-lfs',
        'rsync',
        # 'rabbitmq',
    ]
    """
    Packages that are needed for all windows nodes, please don't remove any
    from this default set.
    """

    qol_packages : List[str] = [
        'firefox',
        'chocolateygui',
        'notepadplusplus',
        'foxitreader',
        'tess',
        'freecad',
        'tortoisegit',
    ]
    """
    Quality of life packages that make actually using a worker node
    bearable.
    """


# Add to the configuration manager
Config.register(
    WorkerSetupConfig,
    interpolation_key = "win_setup",
    conf_file = "win_setup.conf.yaml",
    conf_deps = [],
)
