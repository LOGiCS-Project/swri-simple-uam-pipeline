from attrs import define, field
from .manager import Config
from .path_config import PathConfig
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
        'rsync',
        'nssm',
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
        # 'openmodelica',
    ]
    """
    Chocolatey packages needed for a windows worker node.
    """

    worker_pip_packages : List[str] = [
        # Direct2Cad
        'psutil',
        'parea',
        'numpy',
        'pyyaml',
        'trimesh',
        'matplotlib',
        'triangle',
        'scipy',
        'python-dateutil',
        'gremlinpython',
    ]
    """
    Pip packages needed for a windows D2C worker node.
    """

    license_dep_packages : List[str] = [
    ]
    """
    Chocolatey packages needed for a windows license server node.
    """

    graph_dep_packages : List[str] = [
        'openjdk11',
        'nssm',
    ]
    """
    Chocolatey packages needed for a windows graph server node.
    """

    fdm_dep_packages : List[str] = [
        'msys2',
        'dos2unix',
    ]
    """
    Chocolatey packages needed for a windows FDM worker node.
    """

    fdm_msys2_packages : List[str] = [
        'base-devel',
        'mingw-w64-x86_64-toolchain',
        'gcc',
        'gcc-fortran',
        'python',
        'autotools',
    ]
    """
    Packages to install on the FDM worker's msys2 environment.
    """

    qol_packages : List[str] = [
        'firefox',
        'notepadplusplus',
        'foxitreader',
        'tess',
        'freecad',
    ]
    """
    Quality of life chocolatey packages that make actually using a windows
    node bearable.
    """

# Add to the configuration manager
Config.register(
    WinSetupConfig,
    interpolation_key = "win_setup",
    conf_file = "win_setup.conf.yaml",
    conf_deps = [PathConfig],
)
