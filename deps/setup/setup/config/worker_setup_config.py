from attrs import define, field
from util.config import Config
from typing import List

@define
class WorkerSetupConfig():
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html
    """

    choco_dep_packages : List[str] = [
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
    Packages that are needed for worker setup, please only add items to the
    default set.
    """

    choco_qol_packages : List[str] = [
        'firefox',
        'chocolateygui',
        'notepadplusplus',
        'foxitreader',
        'tess',
        # 'atom',
        # 'openscad',
        'freecad',
        'tortoisegit',
    ]
    """
    Quality of life packages that make actually using a worker node
    bearable.
    """

    # pip_packages : List[str] = [
    #     "minio",
    #     "elasticsearch",
    #     "pyyaml",
    # ]
    # """
    # Pip packages needed for the worker nodes to run.
    # """

# Add to the configuration manager
Config.register(
    WorkerSetupConfig,
    interpolation_key = "worker_setup",
    conf_file = "worker_setup.conf.yaml",
    conf_deps = [],
)
