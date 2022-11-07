import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, WinSetupConfig
from simple_uam.util.logging import get_logger
import importlib.resources as resources
import subprocess

log = get_logger(__name__)


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
    'python3': 'python.exe',
    'tortoisegit': 'TortoiseGitMerge.exe', # not really a CLI app but it's a test
    'nssm': 'nssm.exe',
    'msys2': 'msys2.exe',
    'dos2unix': 'dos2unix.exe',
}

@task
def setup(ctx):
    """ Install Chocolatey (idempotent) """

    with resources.path('simple_uam.data.setup','setup.ps1') as choco_setup_script:

        if shutil.which('choco.exe'):
            log.info(
                "Chocolatey executable found, skipping.",
                script=str(choco_setup_script),
            )
        else:
            log.info(
                "Installing Chocolatey.",
                script=str(choco_setup_script),
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

        with resources.path('simple_uam.data.setup','install.ps1') as choco_install_script:
            installed = subprocess.run([
                'powershell',
                '-executionpolicy','bypass',
                '-File',choco_install_script,*pkgs])

    elif len(pkg) <= 0:
        log.warning("No Chocolatey packages specified for install, skipping.")

    else:
        log.info("No Chocolatey packages specified for install, skipping.")
