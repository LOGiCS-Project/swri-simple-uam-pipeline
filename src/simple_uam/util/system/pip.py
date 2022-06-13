import shutil
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Union, List, Optional
from zipfile import ZipFile
import subprocess
import tempfile
import textwrap
import shutil
from urllib.parse import urlparse
import re
from typing import Optional, Union, List

from .backup import archive_files
from ..logging import get_logger

log = get_logger(__name__)

class Pip():
    """
    Static class used to wrap a bunch of pip commands.
    """

    @staticmethod
    def install(*packages : List[str],
                editable : bool = False,
                requirements_file : Union[str,Path,None] = None,
                upgrade : bool = True,
                progress : bool = True,
                quiet : bool = False,
                verbose : bool = False,
                python : Union[str,Path] = "python",
                cwd : Union[str,Path,None] = None):
        """
        Central function that will run pip install.

        Arguments:
          *packages: The pypi name/project_url/local paths for the package(s)
            you're trying to install. Only one argument if using a vcs url or
            a local path.
          editable: If installing from vcs or local dir, should this package be
            installed as editable.
          requirements_file: The requirements file to extract a list of packages
            from. Mutually exclusive with packages.
          upgrade: Upgrade packages in place, mutually exclusive with upgrade.
          progress: Show the progress bar.
          quiet: Run silently
          verbose: Run w/ verbose output.
          python: Which python interpreter do we use?
            Default: Whatever "python" resolves to in the current env.
        """

        if cwd is None:
            cwd = Path.cwd()
        else:
            cwd = Path(cwd)

        if isinstance(python, Path):
            python = str(python.resolve())

        pip_args = list()


        if requirements_file:
            pip_args.append('-r')
            requirements_file = str(Path(requirements_file).resolve())
            pip_args.append(requirements_file)
            if len(packages) != 0:
                raise RuntimeError(
                    "Cannot specify both requirements file and packages.")
            elif editable:
                raise RuntimeError(
                    "Pip can't use a requirements file during editable install.")

        if upgrade:
            pip_args.append("--upgrade")
            if editable:
                raise RuntimeError(
                    "Can't mark an editable pip package for upgrade.")

        if not progress:
            pip_args.append("--progress-bar")
            pip_args.append("off")

        if quiet:
            pip_args.append("--quiet")

        if verbose:
            pip_args.append("--verbose")

        if editable:
            pip_args.append('-e')
            if len(packages) != 1:
                raise RuntimeError(
                    "Pip can only have one local or vcs package" +
                    "during an editable install.")

        return subprocess.run(
            [python, "-m", "pip", "install", *pip_args, *packages],
            cwd=cwd,
        )
