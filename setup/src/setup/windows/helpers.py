
import util.paths.app_dirs as paths
from util.invoke import task, call
from util.config import Config
from util.logging import get_logger
from setup.config import WorkerSetupConfig
from pathlib import Path
from copy import copy
import setup.windows.choco as choco
import shutil
import textwrap
import subprocess
import re
from attrs import define, field
import attrs.converters as conv
from typing import Optional, Union, List

log = get_logger(__name__)

# Dir where we keep downloaded installers
installer_cache_path = paths.cache_dir / 'worker_installers'

@task
def installer_cache(ctx):
    """ Create the cache directory where installers are downloaded. """

    if not installer_cache_path.exists():
        log.info("Creating Installer Cache Dir.", loc=str(installer_cache_path))
        installer_cache_path.mkdir(parents=True)


def download_file(uri : Path, output : Path):
    """
    Downloads a file from the uri to a given location.

    Arguments:
      uri: The address to download from.
      output: The file_path to download to.
    """

    log.info(
        "Downloading file from web",
        uri=uri,
        file_path=str(loc),
    )

    subprocess.run(["wget.exe",uri,"-O",loc,"--show-progress"])

def verify_file(input : Path, md5 : str):
    """
    Verify that the file at input has the given md5 hash.
    """

    log.info(
        "Verifying file checksum  (sorry no progress bar for this one)",
        file_path=str(input),
        md5=md5,
    )
    proc = subprocess.run(["checksum",input,f"-c={md5}"])
    return proc.returncode == 0

def unpack_file(archive : Path, output : Path):
    """ Unpacks archive to output directory. """

    log.info(
        "Unpacking archive",
        archive=str(archive),
        output=str(output),
    )

    subprocess.run(["7z","x",archive,f"-o{str(output)}"])

def run_gui_exe(exe : Path, notes : Optional[str] = None, wait : bool = True):
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

def append_to_file(file_path : Path, lines : List[str]):
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

def get_mac_address() -> str:
    """ Gets the windows machine's mac address via `ipconfig /all` """

    ipconfig = subprocess.run(
        ["ipconfig", "/all"],
        capture_output=True,
        universal_newlines=True,
    )

    regex = re.compile(
        r"\s+Physical Address[.\s]+:\s(([\dA-F]{2}-){5}[\dA-F]{2})",
        flags = re.S & re.MULTILINE,
    )

    match = regex.search(ipconfig.stdout)

    if match:
        return match.group(1)
    else:
        log.warning(
            "Could not find mac address in ipconfig output.",
            regex = regex,
            match = match,
            result = ipconfig.stdout,
        )
        raise RuntimeException("Could not find mac address in ipconfig output.")

@define
class GUIInstaller():
    """
    Wrapper for a GUI install of an application.
    """

    installed_path : Optional[Path] = field(
        converter=conv.optional(Path),
        kw_only = True,
    )
    """
    Path to check for an existing install.
    Will always install if none
    """

    path : Path = field(
        converter=Path,
        kw_only = True,
    )
    """ Installer location (as subdir of install cache) """

    uri : Optional[str] = field(
        kw_only = True,
    )
    """
    URI to download installer from.
    Will prompt user to copy installer into location if none.
    """

    md5 : Optional[str] = field(
        default = None,
        kw_only = True,
    )
    """
    MD5 Hash for verification of installer, will skip if none.
    """

    unpack_dir : Optional[Path] = field(
        default= None,
        converter=conv.optional(Path),
        kw_only = True,
    )
    """
    Dir within install_cache to unpack download into.
    Assume that installer is exe if none.
    """

    exe : Path = field(
        converter=Path,
        kw_only=True,
    )
    """
    The executable to install, assumed to be in installer_cache dir
    """

    @exe.default
    def _exe_default(self):
        if not self.unpack_dir:
            return self.path
        else:
            raise RuntimeError("Must specify exe if unpack_dir is given.")

    instructions : str = field(
        converter = textwrap.dedent,
        kw_only=True,
    )
    """
    Instructions to give the user before running the installer executable.
    """

    @property
    def installer_path(self) -> Path:
        return (installer_cache_path / self.path).resolve()

    @property
    def installer_unpack_dir(self) -> Optional[Path]:
        if self.unpack_dir:
            return (installer_cache_path / self.unpack_dir).resolve()
        else:
            return None

    @property
    def installer_exe(self):
        unpack_exe = self.installer_unpack_dir / self.exe
        base_exe = installer_cache_path / self.exe
        if base_exe.is_relative_to(installer_unpack_dir):
            return base_exe
        else:
            return unpack_exe


    @property
    def invoke_deps(self):
        """
        Return list of dependencies for install task.
        """

        deps = list()
        if self.uri:
            deps.append('wget')
        if self.md5:
            deps.append('checksum')
        if self.unpack_dir:
            deps.append('7zip')
        if deps:
            return [call(choco.install,pkg=deps)]
        else:
            return []

    @property
    def already_installed(self) -> bool:
        if self.installed_path:
            return self.installed_path.exists()
        else:
            return False

    def get_installer(self):

        # If file exists try to verify
        if self.installer_path.exists():
            if self.md5:
                if not verify_file(self.installer_path, self.md5):
                    log.info(textwrap.dedent(
                        """
                        File exists, verifying checksum.
                        """),
                        path=str(self.installer_path),
                    )
                    # file is invalid, delete it
                    self.installer_path.unlink()
            elif not self.md5:
                log.warning(
                    "If installer is broken delete and re-download installer.",
                    installer=str(self.installer_path),
                )

        # If file does not exist, try to download.
        if not self.installer_path.exists():
            if self.uri:
                log.info(
                    textwrap.dedent(
                        """
                        No installer found. Attempting to download file to
                        the following location manually.
                        """
                    ),
                         path=str(self.installer_path),
                )
                download_file(self.uri, self.installer_path)
            else:
                log.exception(
                    textwrap.dedent(
                        """
                        No installer found and no download uri available.
                        Please place installer in the following location:
                        """),
                    path=str(self.installer_path),
                )
                raise RuntimeError("No installer found")

    def get_installer_exe(self) -> Path:

        self.get_installer()

        unpack_dir = self.installer_unpack_dir

        if unpack_dir and not unpack_dir.exists():
            log.info(
                "Unpacking installer files",
                archive=self.installer_path,
                target=unpack_dir,
            )
            unpack_file(self.installer_path, unpack_dir)

        return self.installer_exe

    def run(self):

        if not self.already_installed:

            exe = self.get_installer_exe

            run_gui_exe(exe, self.instructions)
        else:
            log.info(
                "Software already installed, skipping.",
                install_path = self.installed_path,
            )
