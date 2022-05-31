
import util.paths.app_dirs as paths
import shutil
from util.invoke import task, call
from util.config import Config
from util.logging import get_logger
from setup.config import WorkerSetupConfig

import subprocess

log = get_logger(__name__)

# Directory where chocolatey scripts are found
choco_script_dir = paths.repo_dir / 'setup' / 'data'

# Chololatey env bootstrap script
choco_bootstrap_script = choco_script_dir / 'bootstrap_win.ps1'

# Chololatey setup script
choco_setup_script = choco_script_dir / 'setup.ps1'

# Chololatey package install script
choco_install_script = choco_script_dir / 'install.ps1'

# Map of choco packages to executable name for those where it's easy
choco_exe_map = {
    'git': 'git.exe',
    'sed': 'sed.exe',
    'putty': 'PUTTY.exe',
    'checksum': 'checksum.exe',
    '7zip': '7z.exe',
    'rsync': 'rsync.exe',
    'notepadplusplus': 'notepad++.exe',
    'tess': 'tess.exe',
    'atom': 'atom.cmd',
    'wget': 'wget.exe',
}

@task
def setup(ctx):
    """ Install Chocolatey (idempotent) """

    if shutil.which(choco):
        log.info(
            "Chocolatey executable found, skipping.",
            script=choco_setup_script,
        )
    else:
        log.info(
            "Installing Chocolatey.",
            script=choco_setup_script,
        )

        installed = subprocess.run([
            'powershell',
            '-executionpolicy','bypass',
            '-File',choco_setup_script])

@task(setup,iterable=['pkg'])
def install(ctx, pkg):
    """
    Install Choco packages

    Args:
      pkg: Name of the chocolatey package to install, can be provided multiple
           times.
    """
    pkgs = list()
    for p in pkg:
        if p in choco_exe_map and shutil.which(choco_exe_map[p]):
            log.info(
                f"Executable for pkg already installed.",
                pkg=p,
                exe=choco_exe_map[p]
            )
        else:
            pkgs.append(p)


    if len(pkgs) >= 1:
        log.info(f"Installing Chocolatey packages.", pkgs=pkgs)

        installed = subprocess.run([
            'powershell',
            '-executionpolicy','bypass',
            '-File',choco_install_script,*pkg])
    else:
        log.warning("No Chocolatey packages specified for install, skipping.")
