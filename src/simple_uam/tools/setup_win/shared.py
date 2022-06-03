
from pathlib import Path

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, WinSetupConfig
from simple_uam.util.logging import get_logger

from . import choco
from .helpers import GUIInstaller, append_to_file, get_mac_address

import subprocess

log = get_logger(__name__)

global_dep_pkg_list = Config[WinSetupConfig].global_dep_packages

@task(pre=[call(choco.install, pkg=global_pkg_list)])
def global_dep_pkgs(ctx):
    """ Install/Update global Dependencies (idempotent) """

    log.info("Finished Installing Dependency Packages")

qol_pkg_list = Config[WinSetupConfig].qol_packages

@task(pre=[call(choco.install, pkg=qol_pkg_list)])
def qol_pkgs(ctx):
    """ Install/Update Worker QoL Packages (idempotent) """

    log.info("Finished Installing Quality of Life Packages")

@task
def mac_address(ctx):
    """ print the mac address of this machine. """
    print(get_mac_address())
