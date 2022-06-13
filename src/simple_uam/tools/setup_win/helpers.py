import shutil
import subprocess
import textwrap
import re
from attrs import define, field
import attrs.converters as conv
from typing import Optional, Union, List

from pathlib import Path
from copy import copy
from .choco import install
from .shared import installer_cache, installer_cache_path

from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, WinSetupConfig
from simple_uam.util.logging import get_logger
from simple_uam.util.system.windows import download_file, verify_file, unpack_file, \
    run_gui_exe, append_to_file, get_mac_address

log = get_logger(__name__)

@define
class GUIInstaller():
    """
    Wrapper for a GUI install of an application.
    """

    installed_path : Optional[Path] = field(
        default=None,
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
        default=None,
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
        if base_exe.is_relative_to(self.installer_unpack_dir):
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
            return [installer_cache,call(install,pkg=deps)]
        else:
            return [installer_cache]

    @property
    def already_installed(self) -> bool:
        if self.installed_path:
            return self.installed_path.exists()
        else:
            return False

    def get_installer(self):
        """
        Makes sure that the installer is in the correct location or throws
        an error.
        """

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
                        the following.
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

    def run(self, force=False):
        """
        Runs the installer.

        Arguments:
          force: Run the installer even if the application is already installed.
        """


        if not self.already_installed or force:

            exe = self.get_installer_exe()

            run_gui_exe(exe, self.instructions)
        else:
            log.info(
                "Software already installed, skipping.",
                install_path = self.installed_path,
            )
