import shutil
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Union, List, Optional
from zipfile import ZipFile
import subprocess
import tempfile
import shutil
import re

from ..logging import get_logger

log = get_logger(__name__)


def backup_file(
    file_path: Union[Path, str],
    backup_dir: Union[Path, str, None] = None,
    delete: bool = False,
    missing_ok: bool = True,
):
    """
    Makes a backup copy of a file.

    Arguments:
      file_path: The path to file.
      backup_dir: The directory backups are placed in, default is the same dir
        as the file.
      delete: Do we delete the original? (default: False)
      missing_ok: Do we silently ignore if the file is missing? (default: True)
    """

    file_path = Path(file_path)

    if not backup_dir:
        backup_dir = file_path.parent

    backup_dir = Path(backup_dir)

    if file_path.exists():

        count = 1
        time_str = datetime.now().strftime("%Y-%m-%d")
        bak_file = backup_dir.with_name(f"{file_path.name}.{time_str}.bak")

        while bak_file.exists():
            bak_file = backup_dir.with_name(f"{file_path.name}.{time_str}.{count}.bak")
            count += 1

        backup_dir.mkdir(parents=True, exist_ok=True)

        log.info(
            "Creating Backup File.",
            file=file_path,
            backup=bak_file,
            delete_original=delete,
        )

        if delete:
            shutil.move(file_path, bak_file)
        else:
            shutil.copy2(file_path, bak_file)

    elif not missing_ok:

        raise RuntimeError(f"Cannot backup {str(file_path)} file does not exist.")

    else:

        log.info(
            "No file to backup.",
            file=file_path,
            backup=bak_file,
        )

def archive_files(cwd : Union[str,Path],
                  files : List[Union[str,Path]],
                  out : Union[str,Path],
                  missing_ok : bool = False,
):
    """
    Archives the files in `files` to `out`, preserving any structure `files`
    have relative to `cwd`.

    Note: All `files` must either be relative or in a subdir of `cwd`.

    Arguments:
       cwd: Root locations from which we're gathering files.
       files: list of files to archive.
       out: Output zipfile location.
       missing_ok: Do we ignore files that don't exist?
    """

    cwd = Path(cwd).resolve()
    out = Path(out).resolve()

    def make_arc(f : Path) -> Path:
        """
        Get the relative archive file path for a given file.
        """
        if f.is_absolute() and f.is_relative_to(cwd):
            return f.relative_to(cwd)
        elif not f.is_absolute():
            return f
        else:
            err = RuntimeError("Invalid file location")
            log.exception(
                "File not subdir of cwd.",
                file=str(f),
                cwd=str(cwd),
                err=err,
            )
            raise err

    files = [make_arc(Path(f)) for f in files]

    # Iterate through the files to archive, adding them to the zip file as
    # needed.
    with ZipFile(out, 'x') as zf:
        for arc_file in files:
            sys_file = cwd / rel_file
            if not sys_file.exists() and missing_ok:
                pass
            else:
                zf.write(sys_file, arc_file)
