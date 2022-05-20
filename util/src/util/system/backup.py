import shutil
from datetime import datetime
from pathlib import Path
from typing import Union

from util.logging import get_logger

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
