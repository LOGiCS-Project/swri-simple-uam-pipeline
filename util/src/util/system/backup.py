import shutil
from datetime import datetime
from pathlib import Path
from typing import Union
from zipfile import ZipFile
import tempfile
import shutil

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
    def run(src : Union[str,Path],
            dst : Union[src,Path],
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
        """

        Rsync.require()

        src = Path(src)
        dst = Path(dst)

        flags = list()
        if archive:
            flags.append('-a')
        if delete:
            flags.append('--delete')
        if update:
            flags.append('-u')
        if progress:
            flags.append('--progress')
        if verbose:
            flags.append('-v')
        if quiet:
            flags.append('-q')
        if dry_run:
            flags.append('-n')
        if itemize_changes:
            flags.append('-i')
        for pat in exclude:
            flags.append(f'--exclude={pat}')
        for f in exclude_from:
            f = Path(f).resolve()
            flags.append(f'--exclude-from={f}')

        return subprocess.run(
            ['rsync', *flags, src, dst],
            capture_output=capture_output,
            universal_newlines=True if capture_output else None,
        )


    @staticmethod
    def copy_dir(src : Union[str,Path],
                 dst : Union[src,Path],
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

        Rsync.run(
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



    @staticmethod
    def list_changes(src : Union[str,Path],
                     dst : Union[src,Path],
                     exclude : List[str] = [],
                     exclude_from : List[Union[str,Path]] = [],
                     preserve_dirs : bool = False,
                     prune_missing : bool = True,
    ) -> List[Path]:
        """
        Use rsync to generate a list of files changed in dst relative to src.

        Output paths are all given relative to dst.

        Arguments:
          src: source dir
          dst: destination dir
          exclude: patterns for list of files to ignore
          exclude_from: File to read exclude patterns from (great for gitignore)
          preserve_dirs: preserve directories in the output file list.
          prune_missing: remove entries that aren't present in dst.
        """

        process = Rsync.run(
            src=src,
            dst=dst,
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

        # TODO : Parsing and normalizing here.

        # Multiline regex to get paths r'^[*><\.+a-zA-Z\s]{11}\s(.*)$'


        """
            '-i', # itemize changes
        Itemize format: https://caissyroger.com/2020/10/06/rsync-itemize-changes/

        regex = re.compile(
            r"\s+Physical Address[.\s]+:\s(([\dA-F]{2}-){5}[\dA-F]{2})",
            flags=re.S & re.MULTILINE,
        )

        Examples:

            > rsync -an fog-optimizer/ test/ --exclude-from=fog-optimizer/.gitignore --delete -i
            *deleting   foo.bob
            .d..t...... ./
            >f..t...... fog-optimizer.cabal
            cd+++++++++ app/
            >f+++++++++ app/Main.hs

            > rsync -an fog-optimizer/ test/ --exclude-from=fog-optimizer/.gitignore -i
            .d..t...... ./
            >f..t...... fog-optimizer.cabal
            cd+++++++++ app/
            >f+++++++++ app/Main.hs
        """

        raise NotImplementedError()

    @staticmethod
    def archive_changes(ref : Union[str,Path],
                        src : Union[str,Path],
                        out : Union[str,Path]
    ):
        """
        Package any files that are different in src (compared to ref) into
        a zip file at out.

        Arguments:
          ref: The reference directory
          src: The modified directory
          out: The location of the output zip file
        """

        ref = Path(ref)
        src = Path(src)
        out = Path(out)

        changes = Rsync.list_changes(ref, src)
        archive_files(src,changes,out)
