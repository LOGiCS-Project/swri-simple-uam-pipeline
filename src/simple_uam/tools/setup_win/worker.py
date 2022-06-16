from pathlib import Path

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, WinSetupConfig, AuthConfig
from simple_uam.util.logging import get_logger
from simple_uam.util.system import Git, Pip

from . import choco
from .helpers import GUIInstaller, append_to_file, get_mac_address

import subprocess

log = get_logger(__name__)

@task
def pip_pkgs(ctx):
    """
    Install worker pip reqirements.
    """
    raise NotImplementedError()

worker_dep_pkg_list = [
    *Config[WinSetupConfig].global_dep_packages,
    *Config[WinSetupConfig].worker_dep_packages,
]

@task(pre=[call(choco.install, pkg=worker_dep_pkg_list)])
def choco_pkgs(ctx):
    """ Install/Update Worker Node Dependencies. """

    log.info("Finished Installing Dependency Packages")

@task(call(choco.install, pkg=['python3']))
def pip_pkgs(ctx):
    """ Install Worker Node public Pip packages. """

    Pip.install(*Config[WinSetupConfig].worker_pip_packages)

@task(choco_pkgs, pip_pkgs)
def dep_pkgs(ctx):
    """ Install all the hands-free worker node dependencies. """
    pass

# Directory where creo will be installed
creo_path = Path("C:\Program Files\PTC\Creo 5.0.6.0")

# Creo config file we need to edit
creo_config = creo_path / "Common Files" / "text" / "config.pro"

# Lines we need to add to the creo config file
creo_config_edits = [
    "part_mp_calc_ignore_alt_mp no",    # Part of base instructions
    "suppress_license_loss_dialog yes", # Needed for Direct2Cad
]

creo_installer = GUIInstaller(
    installed_path=creo_path,
    path = 'MED-100WIN-CD-420_5-0-6-0_Win64.zip',
    uri = "https://static.jelloraptor.com/logics_bins/E83683C32F4D04F1DA6ED62EE2C63436.zip",
    md5 = "E83683C32F4D04F1DA6ED62EE2C63436",
    unpack_dir = 'creo_5_install',
    exe = 'setup.exe',
    instructions="""
    ## Installing Creo 5.6 ##

    Notes:

      - You can skip licensing if needed, but a license must
        will be needed eventually for setup to work.

      - If you're using a license server you should enter something
        in the form `<port>@<ip>` when asked for a license.
        (e.g. "7788@10.0.20.142", "7788" is the default port)

      - The license Host-ID is the same as your mac address
        Which can be found by running `ipconfig /all` under
        the 'Physical Address' field.

      - During 'Application Selection':

        - Enable the JLink adapter for Creo Parameteric under:

          Customize.. -> Creo Parametric -> API Toolkits -> Creo Object TOOLKIT for Java and JLink

          See this link for more detailed instructions: http://simplifiedlogic.com/how-to-install-jlink-for-creo

          Note: The installer hangs for a moment when you confirm, give it a few seconds.

        - Consider disabling all the diagnostic reporting.
    """,
)


@task(pre=creo_installer.invoke_deps)
def creo(ctx, force=False):
    """
    Install Creo 5.6

    Arguments:
      force: Run the installer even if creo is already installed.
    """
    creo_installer.run(force=force)

    log.info(
        "Making changes to creo config (if needed).",
        file=creo_config,
        lines=creo_config_edits,
    )

    append_to_file(creo_config, creo_config_edits)

openmeta_installer = GUIInstaller(
    installed_path="C:\\Program Files (x86)\META",
    path = "META_v0.22.0_offline.exe",
    uri ="https://releases.metamorphsoftware.com/releases/v0.24.0/META_v0.24.0_offline.exe",
    md5 = "387BFA3CCED034B30855DD4D7AB4EF9B",
    instructions="""## Installing OpenMETA v0.22.0 ##""",
)

@task(pre=openmeta_installer.invoke_deps)
def openmeta(ctx, force=False):
    """
    Install OpenMETA v0.22.0

    Arguments:
      force: Run the installer even if openmeta is already installed.
    """
    openmeta_installer.run(force=force)

matlab_installer = GUIInstaller(
    installed_path="C:\\Program Files\MATLAB\MATLAB Runtime",
    path = 'MATLAB_Runtime_R2020b_Update_7_win64.zip',
    uri = "https://ssd.mathworks.com/supportfiles/downloads/R2020b/Release/7/deployment_files/installer/complete/win64/MATLAB_Runtime_R2020b_Update_7_win64.zip",
    md5 = "03A387C7A1DCEEEECEE870425528D8EC",
    unpack_dir = 'matlab_2020b',
    exe = 'setup.exe',
    instructions="""
    ## Installing Matlab Runtime 2020b ##

    Notes:

      - It takes a while for the installer to pop up
        after you pass the admin prompt. Be patient.

      - Use the default install path:
        'C:\\Program Files\MATLAB\MATLAB Runtime'
    """,
)

@task(pre=matlab_installer.invoke_deps)
def matlab(ctx, force=False):
    """
    Install Matlab Runtime 2020b

    Arguments:
      force: Run the installer even if matlab is already installed.
    """
    matlab_installer.run(force=force)

# Directory where chocolatey scripts are found
setup_script_dir = Config[PathConfig].repo_data_dir / 'setup'

# Chololatey env bootstrap scrip
disable_ieesc_script = setup_script_dir / 'disable_ieesc.ps1'

@task
def disable_ieesc(ctx):
    """
    Disable Internet Explorer Enhanced Security (Server 2019 only).

    These are the bloody annoying

    Look at the following links for other methods to disable IEESC on other
    versions of windows or via the GUI.
      - https://www.wintips.org/how-to-disable-internet-explorer-enhanced-security-configuration-in-server-2016/
      - https://www.casbay.com/guide/kb/disable-enhanced-security-configuration-for-internet-explorer-in-windows-server-2019-2016
    """

    log.info(
        "Disabling IE Enhanced Security .",
        script=str(disable_ieesc_script),
    )

    installed = subprocess.run([
        'powershell',
        '-executionpolicy','bypass',
        '-File',disable_ieesc_script])

creopyson_dir = Config[PathConfig].work_dir / 'creopyson'
""" Directory with creopyson repo. """

creopyson_repo = "https://git.isis.vanderbilt.edu/SwRI/creoson/creopyson.git"

creopyson_branch = "main"

@task(pre=[call(choco.install, pkg=['python3'])])
def creopyson(ctx, prompt=True, quiet=False, verbose=False):
    """
    Clones/updates the creopyson repository and installs the python library
    globally with pip.

    Arguments:
      prompt: Prompt for a password on initial git clone.
      quiet: Run in quiet mode.
      verbose: Run in verbose mode.
    """

    #### Git ####

    git_args = dict(
        repo_uri = creopyson_repo,
        deploy_dir = creopyson_dir,
        branch = creopyson_branch,
        password_prompt = prompt,
        remote_user = Config[AuthConfig].isis_user,
        remote_pass = Config[AuthConfig].isis_token,
        quiet = quiet,
        verbose = verbose,
        mkdir = True
    )

    if not quiet:
        log.info("Running git clone/pull for creopyson.",**git_args)

    Git.clone_or_pull(**git_args)

    #### Pip ####

    pip_args = dict(
        editable = True,
        upgrade = False,
        quiet = quiet,
        verbose = verbose,
        cwd = creopyson_dir,
    )

    if not quiet:
        log.info("Running pip install w/ local package.",
                 package=creopyson_dir,
                 **pip_args,
        )

    Pip.install(creopyson_dir, **pip_args)
