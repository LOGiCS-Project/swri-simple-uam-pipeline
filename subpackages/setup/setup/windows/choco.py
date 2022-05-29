
import util.paths.app_dirs as paths
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


@task
def setup(ctx):
    """ Install Chocolatey (idempotent) """

    log.info(
        "Installing Chocolatey if needed.",
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

    if len(pkg) >= 1:
        log.info(f"Installing Chocolatey packages.", pkgs=pkg)

        installed = subprocess.run([
            'powershell',
            '-executionpolicy','bypass',
            '-File',choco_install_script,*pkg])
    else:
        log.warning("No Chocolatey packages specified for install, skipping.")
