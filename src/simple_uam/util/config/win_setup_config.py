from attrs import define, field
from .manager import Config
from typing import List

@define
class WinSetupConfig():
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
    Packages that are needed for all windows nodes, please don't remove any
    from this default set.
    """

    broker_dep_packages : List[str] = [
        'rabbitmq',
    ]
    """
    Chocolatey packages needed for a windows broker node.
    """

    worker_dep_packages : List[str] = [
        'openjdk11',
        'openmodelica',
        'rsync',
    ]
    """
    Chocolatey packages needed for a windows worker node.
    """

    worker_pip_packages : List[str] = [
        # Direct2Cad
        'psutil',
        # 'creopyson', # Need to use the creopyson from the swri repo
        'numpy',
        # Craidl
        'gremlinpython',
    ]
    """
    Pip packages needed for a windows worker node.
    """


    license_dep_packages : List[str] = [
    ]
    """
    Chocolatey packages needed for a windows license server node.
    """

    graph_dep_packages : List[str] = [
    ]
    """
    Chocolatey packages needed for a windows graph server node.
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
    Quality of life packages that make actually using a windows node
    bearable.
    """

# Add to the configuration manager
Config.register(
    WinSetupConfig,
    interpolation_key = "win_setup",
    conf_file = "win_setup.conf.yaml",
    conf_deps = [],
)
