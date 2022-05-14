

import util.paths.app_dirs as paths
from util.invoke import task
from util.config import Config
from util.logging import get_logger
from setup.config import WorkerSetupConfig

import subprocess

log = get_logger(__name__)

# Directory where chocolatey scripts are found
choco_script_dir = paths.repo_dir / 'setup' / 'data'

# Chololatey setup script
choco_setup_script = choco_script_dir / 'setup.ps1'

# Chololatey package install script
choco_install_script = choco_script_dir / 'install.ps1'

@task
def install(ctx):
    """ Install Chocolatey (idempotent) """

    log.info(
        "Installing Chocolatey if needed.",
        script=choco_setup_script,
    )

    installed = subprocess.run([
        'powershell',
        '-executionpolicy','bypass',
        '-File',choco_setup_script])

def install_pkg(*pkgs):
    """ Install Choco packages """

    log.info(f"Installing Chocolatey packages.", pkgs=pkgs)

    installed = subprocess.run([
        'powershell',
        '-executionpolicy','bypass',
        '-File',choco_install_script,*pkgs])

@task(install)
def install_deps(ctx):
    """ Install/Update Worker Dependencies (idempotent) """

    log.info(f"Installing worker Chocolatey package dependencies")

    install_pkg(*Config[WorkerSetupConfig].choco_dep_packages)

@task(install)
def install_qol(ctx):
    """ Install/Update Worker QoL Packages (idempotent) """

    log.info(f"Installing worker quality of life packages.")

    install_pkg(*Config[WorkerSetupConfig].choco_qol_packages)

@task(install_deps, install_qol, default=True)
def install_all(ctx):
    """ Install Chocolatey and all packages. (idempotent) """
    pass

@task(install_qol)
def activate_poshgit(ctx):
    """ Activates PoshGit after it's installed """
    if 'poshgit' in Config[WorkerSetupConfig].choco_qol_packages:
        log.info(
            """
            Running PoshGit activation command, please restart all shells.
            """
        )

        subprocess.run(
            ["powershell",
             "-Command",
             f"& {{ Add-PoshGitToProfile -AllHosts }}"]
        )
    else:
        log.warning(
            """
            PoshGit is not in qol packages, skipping activation.
            """
        )
