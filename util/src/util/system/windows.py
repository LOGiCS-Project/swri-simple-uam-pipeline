import re
import shutil
import subprocess
import textwrap
from copy import copy
from pathlib import Path
from typing import List, Optional

from util.logging import get_logger

log = get_logger(__name__)


def download_file(uri: Path, output: Path):
    """
    Downloads a file from the uri to a given location.

    Arguments:
      uri: The address to download from.
      output: The file_path to download to.
    """

    log.info(
        "Downloading file from web",
        uri=uri,
        file_path=str(output),
    )

    subprocess.run(["wget.exe", uri, "-O", output, "--show-progress"])


def verify_file(input: Path, md5: str):
    """
    Verify that the file at input has the given md5 hash.
    """

    log.info(
        "Verifying file checksum  (sorry no progress bar for this one)",
        file_path=str(input),
        md5=md5,
    )
    proc = subprocess.run(["checksum", input, f"-c={md5}"])
    return proc.returncode == 0


def unpack_file(archive: Path, output: Path):
    """Unpacks archive to output directory."""

    log.info(
        "Unpacking archive",
        archive=str(archive),
        output=str(output),
    )

    subprocess.run(["7z", "x", archive, f"-o{str(output)}"])


def run_gui_exe(exe: Path, notes: Optional[str] = None, wait: bool = True):
    """Runs the (windows) gui executable `exe` after displaying `notes`"""

    log.info(
        "Running GUI Executable",
        executable=exe,
    )

    if notes:
        print(textwrap.dedent(notes))

    if wait:
        input(f"\n\nHit Enter To Start Executable: {exe}")

    subprocess.run(["powershell", "-Command", f'& {{ Start-Process "{exe}" -Wait}}'])


def append_to_file(file_path: Path, lines: List[str]):
    """Appends lines to file if they aren't already in the file."""

    lines = copy(lines)

    # Filter out lines already in the file
    with file_path.open("r") as f:
        file_lines = f.readlines()
        lines = [line for line in lines if line not in file_lines]

    # Write out new lines if needed
    if lines != []:

        # Save Backup
        backup_file = file_path.with_stem(file_path.stem + ".bak")
        backup_file.unlink(missing_ok=True)
        shutil.copy2(file_path, backup_file)

        # Append Lines
        with file_path.open("a") as f:
            lines = [line + "\n" for line in lines]
            f.writelines(lines)


def get_mac_address() -> str:
    """Gets the windows machine's mac address via `ipconfig /all`"""

    ipconfig = subprocess.run(
        ["ipconfig", "/all"],
        capture_output=True,
        universal_newlines=True,
    )

    regex = re.compile(
        r"\s+Physical Address[.\s]+:\s(([\dA-F]{2}-){5}[\dA-F]{2})",
        flags=re.S & re.MULTILINE,
    )

    match = regex.search(ipconfig.stdout)

    if match:
        return match.group(1)
    else:
        log.warning(
            "Could not find mac address in ipconfig output.",
            regex=regex,
            match=match,
            result=ipconfig.stdout,
        )
        raise RuntimeException("Could not find mac address in ipconfig output.")
