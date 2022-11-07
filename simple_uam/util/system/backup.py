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

def get_backup_name(
    file_path: Union[Path, str],
    backup_dir: Union[Path, str, None] = None,
):
    """
    Finds a valid name for the backup file.

    Arguments:
      file_path: The path to file. This doesn't have to exist.
      backup_dir: The directory backups are placed in, default is the same dir
        as the file.
    """

    file_path = Path(file_path)
    bak_name = lambda s: f"{file_path.stem}{s}{''.join(file_path.suffixes)}"

    if not backup_dir:
        backup_dir = file_path.parent

    backup_dir = Path(backup_dir)

    count = 1
    time_str = datetime.now().strftime("%Y-%m-%d")
    bak_file = backup_dir / bak_name(f".{time_str}.bak")

    while bak_file.exists():
        bak_file = backup_dir / bak_name(f".{time_str}.{count}.bak")
        count += 1

    return bak_file


def backup_file(
    file_path: Union[Path, str],
    backup_dir: Union[Path, str, None] = None,
    delete: bool = False,
    missing_ok: bool = True,
    is_dir : bool = False,
    archive_dir : bool = True,
):
    """
    Makes a backup copy of a file.

    Arguments:
      file_path: The path to file.
      backup_dir: The directory backups are placed in, default is the same dir
        as the file.
      delete: Do we delete the original? (default: False)
      missing_ok: Do we silently ignore if the file is missing? (default: True)
      is_dir: Is the file a directory? (default: False)
      archive_dir: if we have a directory, should the backup be a zip archive?
        (default: True)
    """

    file_path = Path(file_path)

    if not backup_dir:
        backup_dir = file_path.parent

    backup_dir = Path(backup_dir)
    bak_file = get_backup_name(file_path, backup_dir)

    if file_path.exists():

        backup_dir.mkdir(parents=True, exist_ok=True)

        log.info(
            "Creating Backup File.",
            file=str(file_path),
            backup=str(bak_file),
            delete_original=delete,
        )

        if file_path.is_dir() and not is_dir:
            raise RuntimeError(
                f"Cannot backup {str(file_path)} since it is a directory and is_dir is false."
            )
        elif file_path.is_file() and is_dir:
            raise RuntimeError(
                f"Cannot backup {str(file_path)} since it is a file and is_dir is true."
            )
        elif not file_path.is_file() and not file_path.is_dir():
            raise RuntimeError(
                f"Cannot backup {str(file_path)} since it is neither a file nor a directory."
            )

        if not is_dir:
            if delete:
                shutil.move(file_path, bak_file)
            else:
                shutil.copy2(file_path, bak_file)
        elif archive_dir: # and is_dir
            files = file_path.glob("**")
            archive_name = file_path.with_suffix(f"{file_path.suffix}.zip")
            archive_bak = get_backup_name(archive_name, backup_dir)
            archive_files(file_path, files, archive_bak)

            if delete:
                shutil.rmtree(file_path)

        else: # elif is_dir and not archive_dir
            if delete:
                shutil.move(file_path, bak_file)
            else:
                shutil.copytree(file_path, bak_file)

        return bak_file

    elif not missing_ok:

        raise RuntimeError(f"Cannot backup {str(file_path)} file does not exist.")

    else:

        log.info(
            "No file to backup.",
            file=str(file_path),
            backup=str(bak_file),
        )

        return None

def archive_file_mapping(files : Dict[Union[str,Path],Union[str,Path]],
                         out : Union[str,Path],
                         cwd : Union[None,str,Path] = None,
                         missing_ok : bool = False,
                         delete_existing : bool = False,
):
    """
    Uses the mapping `files`, from input file locations to archive locations,
    constructs a zip file.

    Arguments:
       files: dictionary from system files to archive location. Archive location
         must be a relative path.
       out: Output zipfile location.
       cwd: The working directory which is taken as the root for all relative
         system files and the output zipfile. (Default: cwd)
       missing_ok: Do we ignore files that don't exist?
       delete_existing: Delete a preexisting archive at out if True, otherwise
         make backup. (Default: False)
    """

    if not cwd:
        cwd = Path.cwd()
    cwd = Path(cwd).resolve()

    out = Path(out)
    if not out.is_absolute():
        out = cwd / out
    out = out.resolve()

    normed_files = dict()

    for sys_file, arc_file in files.items():

        sys_file = Path(sys_file)
        if not sys_file.is_absolute():
            sys_file = cwd / sys_file
        sys_file = sys_file.resolve()

        arc_file = Path(arc_file)

        if arc_file.is_absolute():
            err = RuntimeError(
                f"Provided archive file loc `{str(arc_file)}` must be a "
                "relative path."
            )

            log.error(
                "Archive file loc must be relative path.",
                sys_file=str(sys_file),
                arc_file=str(arc_file),
                cwd=str(cwd),
                err=err,
            )

            raise err

        normed_files[sys_file] = arc_file

    if out.exists() and delete_existing:
        log.info(
            "Archive already exists, deleting.",
            archive_file=str(out),
        )
        out.unlink()
    elif out.exists():
        log.info(
            "Archive already exists, backing up before creating a new one.",
            archive_file=str(out),
        )
        backup_file(out, delete=True)

    # Iterate through the files to archive, adding them to the zip file as
    # needed.
    with ZipFile(out, 'x') as zf:
        for sys_file, arc_file in normed_files.items():
            if not sys_file.exists() and missing_ok:
                pass
            else:
                zf.write(sys_file, arc_file)

def archive_file_list_to_file_mapping(cwd : Union[str,Path],
                                      files : List[Union[str,Path]],
):
    """
    Convert from a list of files to archive in a directory to a map of
    system file location and archive file location pairs.
    Preserves any structure `files` has relative to `cwd`.

    Note: All `files` must either be relative or in a subdir of `cwd`.

    Arguments:
       cwd: Root locations from which we're gathering files.
       files: list of files to archive.
    """

    cwd = Path(cwd).resolve()
    file_map = dict()

    for sys_file in files:

        sys_file = Path(sys_file)
        arc_file = sys_file

        if sys_file.is_absolute() and sys_file.is_relative_to(cwd):
            arc_file = sys_file.relative_to(cwd)
        elif not sys_file.is_absolute():
            sys_file = cwd / sys_file
        else:
            err = RuntimeError("Invalid file location")
            log.exception(
                "File not subdir of cwd.",
                file=str(sys_file),
                cwd=str(cwd),
                err=err,
            )
            raise err

        file_map[sys_file] = arc_file

    return file_map


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

    # NOTE: This mostly just exists so that the original API doesn't break
    #       after we switched to a version that uses an explicit map.
    file_map = archive_file_list_to_file_mapping(cwd, files)
    archive_file_mapping(file_map, out, missing_ok = missing_ok)

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

    # delete output here incase output == input
    output_file.unlink(missing_ok=True)

    log.info(
        "Writing configuration output.",
        output_file=str(output_file))

    with output_file.open('w') as file:
        file.write(filedata)
