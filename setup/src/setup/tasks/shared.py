
import util.paths.app_dirs as paths
from pathlib import Path
from util.invoke import task, call
from util.config import Config
from util.logging import get_logger
from setup.config import WorkerSetupConfig
import setup.windows.choco as choco
from setup.windows.helpers import GUIInstaller, append_to_file, get_mac_address

import subprocess

log = get_logger(__name__)

dep_pkg_list = Config[WorkerSetupConfig].choco_dep_packages

@task(pre=[call(choco.install, pkg=dep_pkg_list)])
def dep_pkgs(ctx):
    """ Install/Update Worker Dependencies (idempotent) """

    log.info("Finished Installing Dependency Packages")

qol_pkg_list = Config[WorkerSetupConfig].choco_qol_packages

@task(pre=[call(choco.install, pkg=qol_pkg_list)])
def qol_pkgs(ctx):
    """ Install/Update Worker QoL Packages (idempotent) """

    log.info("Finished Installing Quality of Life Packages")

@task(dep_pkgs, qol_pkgs)
def all_pgks(ctx):
    """ Install Dependency and Qol Packages (idempotent) """
    log.info("Finished Installing Chocolatey Packages")

@task
def mac_address(ctx):
    """ print the mac address of this machine. """
    log.info(
        "Getting Mac Address via ipconfig",
        mac_addr = get_mac_address(),
    )
