
from pathlib import Path

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, WinSetupConfig
from simple_uam.util.logging import get_logger

from .choco import install
from simple_uam.util.system.windows import append_to_file, get_mac_address

import subprocess

log = get_logger(__name__)

global_pkg_list = Config[WinSetupConfig].global_dep_packages

@task(pre=[call(install, pkg=global_pkg_list)])
def global_pkgs(ctx):
    """ Install/Update Global Dependencies """

    log.info("Finished Installing Dependency Packages")

qol_pkg_list = Config[WinSetupConfig].qol_packages

@task(pre=[call(install, pkg=qol_pkg_list)])
def qol_pkgs(ctx):
    """ Install/Update Worker QoL Packages """

    log.info("Finished Installing Quality of Life Packages")

@task
def mac_address(ctx):
    """ print the mac address of this machine. """
    print(get_mac_address())

# Dir where we keep downloaded installers
installer_cache_path = Config[PathConfig].cache_dir / 'simple_uam_installers'

@task
def installer_cache(ctx):
    """ Create the cache directory where installers are downloaded. """

    if not installer_cache_path.exists():
        log.info("Creating Installer Cache Dir.", loc=str(installer_cache_path))
        installer_cache_path.mkdir(parents=True)

@task
def clear_cache(ctx):
    """ Delete the installer cache. """

    if not installer_cache_path.exists():
        return

    ret = input(
        f'Delete the entire cache at {str(installer_cache_path)} (y/N):'
    )

    if ret == 'N':
        print("Skipping deletion")
    elif ret != 'y':
        print("Please enter 'y' or 'N', skipping deletion.")
    else:
        shutil.rmtree(installer_cache_path)
