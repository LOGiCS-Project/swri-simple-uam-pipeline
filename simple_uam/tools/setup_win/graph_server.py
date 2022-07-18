from pathlib import Path

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, WinSetupConfig
from simple_uam.util.logging import get_logger

from . import choco
from .helpers import GUIInstaller, append_to_file, get_mac_address

import subprocess

log = get_logger(__name__)

graph_dep_pkg_list = [
    *Config[WinSetupConfig].global_dep_packages,
    *Config[WinSetupConfig].graph_dep_packages,
]

@task(pre=[call(choco.install, pkg=graph_dep_pkg_list)])
def choco_pkgs(ctx):
    """ Install/Update Graph Stub Server Dependencies """

    log.info("Finished Installing Dependency Packages")
