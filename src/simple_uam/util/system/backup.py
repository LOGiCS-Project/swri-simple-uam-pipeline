import shutil
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Union, List, Optional, Dict
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
    bak_file = file_path.with_name(f"{file_path.name}.bak")

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
            file=str(file_path),
            backup=str(bak_file),
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
            file=str(file_path),
            backup=str(bak_file),
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

def configure_file(input_file : Union[str,Path],
                   output_file : Union[str, Path],
                   replacements : Dict[str,str] = {},
                   exist_ok : bool = False,
                   backup : bool = True,
                   backup_dir : Union[str,Path,None] = None):
    """
    Will "configure" and install a file by performing a set of string
    replacements and moving it to a final location.

    Arguments:
       input_file: The input_file to use.
       output_file: The output location to place the configured file.
       replacements: The string to find and replace in the input file.
       exist_ok: If true will overwrite an existing file.
       backup: If overwriting a file do we create a backup?
       backup_dir: Place backups in this directory, if not specified defaults
         to output directory.
    """

    input_file = Path(input_file).resolve()
    output_file = Path(output_file).resolve()

    # Verification
    if not exist_ok and output_file.exists():
        err = RuntimeError("Target file already exists.")
        log.exception(
            "Cannot configure file because output already exists.",
            err = err,
            input_file = input_file,
            output_file = output_file,
        )
        raise err

    # Backup
    if backup:
        backup_file(
            output_file,
            backup_dir = backup_dir,
        )

    # Delete
    output_file.unlink(missing_ok=True)

    log.info(
        "Reading configuration input.",
        input_file = str(input_file))

    with input_file.open('r') as file :
        filedata = file.read()

    for find, replace in replacements.items():
        log.info(
            "Performing configuration replacement.",
            find=find,
            replace=replace,
        )
        filedata = filedata.replace(find, replace)

    log.info(
        "Writing configuration output.",
        output_file=str(output_file))

    with output_file.open('w') as file:
        file.write(filedata)
