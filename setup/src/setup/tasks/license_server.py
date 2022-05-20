
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

@task
def disable_firewall(ctx):
    """
    Disable the Windows Server firewall. (ONLY USE ON PRIVATE NETWORK)

    This disables the firewall for all port and connections. Do not use this
    if the license server can be accessed by any untrusted devices.
    """


    log.info(
        "Disabling Windows Firewall.",
    )

    installed = subprocess.run([
        'NetSh', 'Advfirewall', 'set', 'allprofiles', 'state', 'off'])

flexnet_installer = GUIInstaller(
    installed_path="C:\\Program Files\PTC\FLEXnet Admin License Server",
    path = 'flexnetadmin64_11.7.1.0.zip',
    uri = "http://download.ptc.com/download2/products/FLEXnet/flexnetadmin64_11.17.1.0.zip",
    md5 = "87C53D75D048059B73582BF4C580A3B3",
    unpack_dir = 'flexnetadmin64',
    exe = 'setup.exe',
    instructions="""
    ## Installing Flexnet License Server ##

    Notes:

      - Have your server license ready, the installer cannot complete without
        it.

      - You can find your host id by using the `mac-address` command from the
        executable you used to launch this.
    """,
)

@task(pre=flexnet_installer.invoke_deps)
def flexnet(ctx):
    """ Install Flexnet License Server """
    flexnet_installer.run()
