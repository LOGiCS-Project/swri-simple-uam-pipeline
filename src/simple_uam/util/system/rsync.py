import shutil
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Union, List, Optional
from zipfile import ZipFile
import subprocess
import tempfile
import shutil
import re

from .backup import archive_files
from ..logging import get_logger

log = get_logger(__name__)

class Rsync():
    """
    Static class used to wrap a bunch of rsync commands.
    """

    @staticmethod
    def which():
        """
        Returns the rsync executable if it exists or None otherwise.
        """

        return shutil.which("rsync")

    @staticmethod
    def require():
        """
        Raises an error if rsync isn't installed.
        """
        if not Rsync.which():
            raise RuntimeError(
                "Rsync not found. Please install rsync and ensure it's on PATH."
            )

    @staticmethod
    def norm_path(path : Union[str,Path],
                  is_dir : Optional[bool]) -> str:
        """
        Rsync on windows is weird about paths, this will format an input path
        appropriately.

        Arguments:
          path: The Path to format.
          is_dir: if True appends dir suffix to path.
                  if False does not append suffix,
                  if None will attempt to detect based on existing file.

        Returns:
          An absolute path string suitable as a cmd line arg for rsync.
        """

        path = Path(path).resolve()

        if is_dir == None and path.exists() and not path.is_dir():
            is_dir = False
        else:
            is_dir = True

        path_str = path.as_posix()

        win_dir = re.match(r'([A-z]):(.*)')

        # Uses cygwin style absolute paths for rsync.
        if win_dir and isinstance(path,WindowsPath):
            path_str = f"/cygdrive/{win_dir[1]}{win_dir[2]}"

        # Rsync on windows uses the trailing '/' to distingush between a file
        # and a directory, features like delete don't work if rsync thinks
        # src is a file.
        if is_dir and not path_str.endswith('/'):
            path_str = path_str + '/'

        return path_str

    @classmethod
    def run(cls,
            src : Union[str,Path],
            dst : Union[str,Path],
            *,
            exclude : List[str] = [],
            exclude_from : List[Union[str,Path]] = [],
            archive : bool = True,
            delete : bool = True,
            update : bool = False,
            progress : bool = False,
            verbose : bool = False,
            quiet : bool = False,
            dry_run : bool = False,
            itemize_changes : bool = False,
            capture_output : bool = False,
            links : bool = False,
            times : bool = False,
            owner : bool = False,
            group : bool = False,
            perms : bool = False,
            recursive : bool = False,
    ) -> subprocess.CompletedProcess:
        """
        Run rsync with args return the completed process object.

        Arguments:
          src: source dir
          dst: destination dir
          exclude: patterns for list of files to ignore
          exclude_from: File to read exclude patterns from (great for gitignore)
          archive: Run in archive mode,
          delete: delete files in dst that aren't in src
          update: don't overwrite files that are newer in dst than src
          progress: show progress bar
          verbose: run in verbose mode
          quite: supress non-error messages.
          dry_run: make no changes
          itemize_changes: print a list of all changes to stdout
          capture_output: do we capture stdout?
          links: When symlinks are encountered, recreate the symlink on the
            destination.
          recursive: This tells rsync to copy directories recursively.
          times: preserve modification times.
          owner: preserve owner (super-user only)
          group: preserve group
          perms: preserve permissions
        """

        Rsync.require()

        src = Path(src)
        dst = Path(dst)

        if not (src.exists() and src.is_dir()):
            err = RuntimeError("Rsync src isn't a dir.")
            log.exception(
                "Rsync src argument must be a dir.",
                src=str(src),
                exists=src.exists(),
                is_dir=src.is_dir(),
                err=err,
            )
            raise err
        else:
            src = src.resolve()

        if not (dst.exists() and dst.is_dir()):
            err = RuntimeError("Rsync dst isn't a dir.")
            log.exception(
                "Rsync dst argument must be a dir.",
                dst=str(dst),
                exists=dst.exists(),
                is_dir=dst.is_dir(),
                err=err,
            )
            raise err
        else:
            dst = dst.resolve()

        flags = list()
        if archive:
            flags.append('--archive')
        if recursive:
            flags.append('--recursive')
        if links:
            flags.append('--links')
        if delete:
            flags.append('--delete')
        if update:
            flags.append('--update')
        if owner:
            flags.append('--owner')
        if perms:
            flags.append('--perms')
        if group:
            flags.append('--owner')
        if progress:
            flags.append('--group')
        if times:
            flags.append('--times')
        if verbose:
            flags.append('--verbose')
        if quiet:
            flags.append('--quiet')
        if dry_run:
            flags.append('--dry_run')
        if itemize_changes:
            flags.append('--itemize_changes')
        for pat in exclude:
            flags.append(f'--exclude={pat}')
        for f in exclude_from:
            f = cls.norm_path(Path(f).resolve())
            flags.append(f'--exclude-from={f}')

        return subprocess.run(
            ['rsync', *flags, cls.norm_path(src), cls.norm_path(dst)],
            capture_output=capture_output,
            universal_newlines=True if capture_output else None,
        )


    @classmethod
    def copy_dir(cls,
                 src : Union[str,Path],
                 dst : Union[str,Path],
                 exclude : List[str] = [],
                 exclude_from : List[Union[str,Path]] = [],
                 delete : bool = True,
                 update : bool = False,
                 progress : bool = False,
                 verbose : bool = False,
                 quiet : bool = False,
    ):
        """
        Use rsync to copy a directory incrementally, dst will be the same
        as src when finished with defaults.

        Arguments:
          src: source dir
          dst: destination dir
          exclude: patterns for list of files to ignore
          exclude_from: File to read exclude patterns from (great for gitignore)
          delete: delete files in dst that aren't in src
          update: don't overwrite files that are newer in dst than src
          progress: show progress bar
          verbose: run in verbose mode
          quiet: supress non-error output
        """

        cls.run(
            src=src,
            dst=dst,
            exclude=exclude,
            exclude_from=exclude_from,
            delete=delete,
            update=update,
            progress=progress,
            verbose=verbose,
            quiet=quiet,
        )

    itemize_regex = re.compile(r'^[*><\.+a-zA-Z\s]{11}\s(.*)$', re.MULTILINE)
    """
    Regex for getting the directories out of the rsync '-i' itemize call.
    See: https://caissyroger.com/2020/10/06/rsync-itemize-changes/
    """

    @classmethod
    def list_changes(cls,
                     ref : Union[str,Path],
                     src : Union[str,Path],
                     exclude : List[str] = [],
                     exclude_from : List[Union[str,Path]] = [],
                     preserve_dirs : bool = False,
                     prune_missing : bool = True,
    ) -> List[Path]:
        """
        Use rsync to generate a list of files changed in dst relative to src.

        Output paths are all given relative to dst.

        Arguments:
          ref: the reference directory
          src: the source dir, to check for changes
          exclude: patterns for list of files to ignore
          exclude_from: File to read exclude patterns from (great for gitignore)
          preserve_dirs: preserve directories in the output file list.
          prune_missing: remove entries that aren't present in dst.
        """

        dst = Path(dst).resolve()

        process = cls.run(
            src=ref,
            dst=src,
            exclude=exclude,
            exclude_from=exclude_from,
            archive=True,
            delete=True,
            update=False,
            progress=False,
            verbose=False,
            dry_run=True,
            itemize_changes=True,
            capture_output=True,
        )

        changes = list()
        for changed in cls.itemize_regex.findall(process.stdout):
            if changed == "./":
                continue

            if not prune_missing or (dst / changed).exists():
                if preserve_dirs or not changed.endswith('/'):
                    changes.append(Path(changed))

        return changes

    @staticmethod
    def archive_changes(ref : Union[str,Path],
                        src : Union[str,Path],
                        out : Union[str,Path],
                        exclude : List[str] = [],
                        exclude_from : List[Union[str,Path]] = [],
    ):
        """
        Package any files that are different in src (compared to ref) into
        a zip file at out.

        Arguments:
          ref: The reference directory
          src: The modified directory
          out: The location of the output zip file
          exclude: patterns for list of files to ignore
          exclude_from: File to read exclude patterns from (great for gitignore)
        """

        ref = Path(ref)
        src = Path(src)
        out = Path(out)

        changes = Rsync.list_changes(
            ref=ref,
            src=src,
            exclude=exclude,
            exclude_from=exclude_from,
        )
        archive_files(src,changes,out)
