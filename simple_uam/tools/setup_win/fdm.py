from pathlib import Path

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, WinSetupConfig, \
    AuthConfig, CorpusConfig
from simple_uam.util.logging import get_logger
from simple_uam.util.system.msys2 import Msys2

from . import choco
import importlib.resources as resources
from .helpers import GUIInstaller, append_to_file, get_mac_address

import subprocess

log = get_logger(__name__)

fdm_dep_pkg_list = [
    *Config[WinSetupConfig].global_dep_packages,
    *Config[WinSetupConfig].fdm_dep_packages,
]

@task(pre=[call(choco.install, pkg=fdm_dep_pkg_list)])
def choco_pkgs(ctx):
    """ Install/Update FDM Worker Node Dependencies. """

    log.info("Finished Installing Dependency Packages")

@task(call(choco.install, pkg=['msys2']))
def msys2_pkgs(ctx):
    """ Install FDM Node pip packages. """

    Msys2.install(*Config[WinSetupConfig].fdm_msys2_packages)

@task(choco_pkgs, msys2_pkgs)
def dep_pkgs(ctx):
    """ Install all the hands-free worker node dependencies. """
    pass
