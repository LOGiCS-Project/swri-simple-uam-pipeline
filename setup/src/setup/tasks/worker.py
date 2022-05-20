
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

      - During 'Application Selection' I disabled all the diagnostic
        reporting.
    """,
)


@task(pre=creo_installer.invoke_deps)
def creo(ctx):
    """ Install Creo 5.6 """
    creo_installer.run()

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
def openmeta(ctx):
    """ Install OpenMETA v0.22.0 """
    openmeta_installer.run()

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
def matlab(ctx):
    """ Install Matlab Runtime 2020b """
    matlab_installer.run()

# Directory where chocolatey scripts are found
setup_script_dir = paths.repo_dir / 'setup' / 'data'

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
