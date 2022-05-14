

import util.paths.app_dirs as paths
from util.invoke import task
from util.config import Config
from util.logging import get_logger
from setup.config import WorkerSetupConfig
import setup.worker.choco as choco
from pathlib import Path
from copy import copy
import shutil
import textwrap
import subprocess

log = get_logger(__name__)

# Dir where we keep downloaded installers
installer_cache = paths.cache_dir / 'worker_installers'

@task
def make_installer_cache(ctx):
    """ Create the cache directory where installers are downloaded. """

    if not installer_cache.exists():
        log.info("Creating Installer Cache Dir.", loc=str(installer_cache))
        installer_cache.mkdir(parents=True)

def download_file(uri, loc):
    """ Downloads a file from the uri to a given location. """

    log.info(
        "Downloading file from web",
        uri=uri,
        file_path=str(loc),
    )

    subprocess.run(["wget.exe",uri,"-O",loc,"--show-progress"])

def verify_file(loc, md5):
    """ Verify that the file at loc has the given md5 hash. """

    log.info(
        "Verifying file checksum  (sorry no progress bar for this one)",
        file_path=str(loc),
        md5=md5,
    )
    proc = subprocess.run(["checksum",loc,f"-c={md5}"])
    return proc.returncode == 0

def unpack_zip(archive, loc):
    """ Unpacks archive to loc. """

    log.info(
        "Unpacking archive",
        archive=str(archive),
        output=str(loc),
    )

    subprocess.run(["7z","x",archive,f"-o{str(loc)}"])

def run_gui_exe(exe, notes = None, wait = True):
    """ Runs the (windows) gui executable `exe` after displaying `notes` """

    log.info(
        "Running GUI Executable",
        executable=exe,
    )

    if notes:
        print(textwrap.dedent(notes))

    if wait:
        input(f"\n\nHit Enter To Start Executable: {exe}")

    subprocess.run(
        ["powershell",
        "-Command",
        f"& {{ Start-Process \"{exe}\" -Wait}}"])

def append_to_file(file_path, lines):
    """ Appends lines to file if they aren't already in the file. """

    lines = copy(lines)

    # Filter out lines already in the file
    with file_path.open('r') as f:
        file_lines = f.readlines()
        lines = [line for line in lines if line not in file_lines]

    # Write out new lines if needed
    if lines != []:

        # Save Backup
        backup_file = file_path.with_stem(file_path.stem + ".bak")
        backup_file.unlink(missing_ok=True)
        shutil.copy2(file_path, backup_file)

        # Append Lines
        with file_path.open('a') as f:
            lines = [line + "\n" for line in lines]
            f.writelines(lines)

### Matlab Setup ###

# Path to final matlab executable
matlab_path = Path("C:\\Program Files\MATLAB\MATLAB Runtime")

# The uri for the matlab installer
matlab_zip_uri = "https://ssd.mathworks.com/supportfiles/downloads/R2020b/Release/7/deployment_files/installer/complete/win64/MATLAB_Runtime_R2020b_Update_7_win64.zip"

# The md5 hash of the matlab installer zip
matlab_zip_md5 = "03A387C7A1DCEEEECEE870425528D8EC"

# The final location of the installer zip
matlab_installer_zip = installer_cache / 'MATLAB_Runtime_R2020b_Update_7_win64.zip'

# The directory into which the zip should be unpacked
matlab_installer_dir = installer_cache / 'matlab_2020b'

# The installer exe when unpacked fully
matlab_installer_exe = matlab_installer_dir / 'setup.exe'

@task(make_installer_cache, choco.install_deps, name='matlab')
def install_matlab(ctx):
    """
    Installs matlab if not already installed, downloads installer if needed.
    """

    if not matlab_path.exists():

        # Download and unpack installer if needed
        if not matlab_installer_exe.exists():

            # If zip already exists, check if correct, otherwise redownload.
            if matlab_installer_zip.exists():

                log.info(textwrap.dedent(
                    """
                    File exists, verifying checksum.
                    """),
                    path=str(matlab_installer_zip),
                )

                if not verify_file(matlab_installer_zip, matlab_zip_md5):
                    matlab_installer_zip.unlink()

            # Download installer zip if needed
            if not matlab_installer_zip.exists():

                log.info(
                    textwrap.dedent(
                        """
                        If the download fails you can place the
                        matlab zip file at the following location manually.
                        """
                    ),
                    path=str(matlab_installer_zip),
                )

                download_file(matlab_zip_uri, matlab_installer_zip)


            # Unpack installer zip so exe exists
            unpack_zip(matlab_installer_zip, matlab_installer_dir)

        # Run the installer
        run_gui_exe(
            matlab_installer_exe,
            notes="""
            ## Installing Matlab Runtime 2020b ##

            Notes:

              - It takes a while for the installer to pop up
                after you pass the admin prompt. Be patient.

              - Use the default install path:
                'C:\\Program Files\MATLAB\MATLAB Runtime'
            """,
        )

### OpenMeta Setup ###

# Directory where the OpenMETA install Lives
openmeta_path = Path("C:\\Program Files (x86)\META")

# The URI for the installer
openmeta_installer_uri = "https://releases.metamorphsoftware.com/releases/v0.24.0/META_v0.24.0_offline.exe"

# The MD5 Hash for the installer
openmeta_installer_md5 = "387BFA3CCED034B30855DD4D7AB4EF9B"

# The post-download location of the installer
openmeta_installer = installer_cache / "META_v0.22.0_offline.exe"

@task(make_installer_cache, choco.install_deps, name='openmeta')
def install_openmeta(ctx):
    """
    Installs openmeta if not already installed, downloads installer if needed.
    """

    if not openmeta_path.exists():

        # If zip already exists, check if correct, otherwise redownload.
        if openmeta_installer.exists():

            log.info(textwrap.dedent(
                """
                File exists, verifying checksum.
                """),
                path=str(openmeta_installer),
            )

            # If invalid delete file
            if not verify_file(openmeta_installer, openmeta_installer_md5):
                openmeta_installer.unlink()


        # Download installer if needed
        if not openmeta_installer.exists():

            log.info(
                textwrap.dedent(
                    """
                    If the download fails you can place the
                    openmeta installer at the following location manually.
                    """
                ),
                     path=str(openmeta_installer),
            )
            download_file(openmeta_installer_uri, openmeta_installer)


        # Run the installer
        run_gui_exe(
            openmeta_installer,
            notes="""
            ## Installing Openmeta ##
            """,
        )

### Creo Setup ###

# Directory where creo will be installed
creo_path = Path("C:\Program Files\PTC\Creo 5.0.6.0")

# Url where creo zip can be found
# NOTE :: This is hosted on a personal server w/ no uptime guarantees
#         Download the Creo5.6 installer from ptc if it's taken down.
creo_zip_uri = "https://static.jelloraptor.com/logics_bins/E83683C32F4D04F1DA6ED62EE2C63436.zip"

# Creo installer zip file
creo_installer_zip = installer_cache / 'MED-100WIN-CD-420_5-0-6-0_Win64.zip'

# Has for the creo installer
creo_installer_md5 = "E83683C32F4D04F1DA6ED62EE2C63436"

# Crea installer directory
creo_installer_dir = installer_cache / 'creo_5_install'

# Creo installer exe
creo_installer_exe = creo_installer_dir / 'setup.exe'

# Creo config file we need to edit
creo_config = creo_path / "Common Files" / "text" / "config.pro"

# Lines we need to add to the creo config file
creo_config_edits = [
    "part_mp_calc_ignore_alt_mp no",
]

@task(make_installer_cache, choco.install_deps, name='creo')
def install_creo(ctx):
    """
    Installs creo if not already installed, downloads installer if needed.
    """

    if not creo_path.exists():

        # Download and unpack installer if needed
        if not creo_installer_exe.exists():

            # If zip already exists, check if correct, otherwise redownload.
            if creo_installer_zip.exists():

                log.info(textwrap.dedent(
                    """
                    File exists, verifying checksum.
                    """),
                    path=str(creo_installer_zip),
                )

                if not verify_file(creo_installer_zip, creo_installer_md5):
                    creo_installer_zip.unlink()

            # Download installer zip if needed
            if not creo_installer_zip.exists():
                log.info(
                    textwrap.dedent(
                        """
                        If the download fails you can place the
                        creo zip file at the following location manually.
                        """
                    ),
                         path=str(creo_installer_zip),
                )
                download_file(creo_zip_uri, creo_installer_zip)

            # Unpack installer zip so exe exists
            unpack_zip(creo_installer_zip, creo_installer_dir)

        # Run the installer
        run_gui_exe(
            creo_installer_exe,
            notes="""
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

    log.info(
        "Making changes to creo config (if needed).",
        file=creo_config,
        lines=creo_config_edits,
    )

    append_to_file(creo_config, creo_config_edits)
