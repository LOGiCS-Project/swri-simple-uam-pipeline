
from typing import List, Tuple, Dict, Optional, Union
from pathlib import Path
from simple_uam.util.logging import get_logger
from simple_uam.util.system import Rsync
import simple_uam.util.system.backup as backup
from simple_uam.util.system.git import Git
from simple_uam.util.exception import contextualize_exception
from simple_uam.worker import actor, message_metadata
from attrs import define,field
from filelock import Timeout, FileLock
from functools import wraps
from datetime import datetime
from copy import deepcopy
import traceback
import subprocess
import platform
import os
import uuid
import socket
import re
import json

log = get_logger(__name__)

def session_op(f):
    """
    Decorator for functions within the workspace that must take place within
    a session and should be added to the log.
    """

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        # NOTE : 'self' here is a Session or child.
        # add start log entry
        result = f(self, *args, **kwargs)
        # add end log entry
        return result

    return wrapper

@define
class Session():
    """
    An object that represents a session within a workspace, provide various
    helpers for managed a bunch of operations, as well as logging and the like.

    Used within a context manager.

    Inherit from this class and add more operations that are specific to a
    particular context.
    """

    number : int = field(
        kw_only=True,
    )
    """ The number of the workspace this object is operating with. """

    reference_dir : Path = field(
        kw_only=True,
        converter=Path,
    )
    """ The reference directory that the work_dir is copied from. """

    @reference_dir.validator
    def _ref_dir_valid(self, attr, val):
        if not val.is_absolute():
            raise RuntimeError("Session init paths must be absolute.")

    work_dir : Path = field(
        kw_only=True,
        converter=Path,
    )
    """ The directory in which the session runs. """

    @work_dir.validator
    def _work_dir_valid(self, attr, val):
        if not val.is_absolute():
            raise RuntimeError("Session init paths must be absolute.")

    _result_archive : Path = field(
        kw_only=True,
    )
    """
    Where the result archive should be written to, after session completion
    the workspace should update this to the final archive location.
    """

    @_result_archive.validator
    def _result_archive_valid(self, attr, val):
        if not val.is_absolute():
            raise RuntimeError("Session init paths must be absolute.")

    @property
    def result_archive(self):
        return self._result_archive

    @result_archive.setter
    def result_archive(self, val):
        self.metadata['result_archive'] = str(val.name)
        self._result_archive = val

    name : str = field(
        default="generic-session",
        kw_only=True,
    )
    """ A name for the type of session being performed. """

    metadata : Dict = field(
        factory=dict,
        kw_only=True,
    )
    """
    The metadata for this session, will be stored in metadata.json in the
    result archive.

    Will be initialized by the Workspace.
    """

    metadata_file : Path = field(
        default=Path("metadata.json"),
        kw_only=True,
    )
    """
    The file in the workdir (and eventually in the results archive) that stores
    the current metadata.
    """

    @metadata_file.validator
    def _meta_file_valid(self, attr, val):
        if val.is_absolute():
            raise RuntimeError("The metadata file must be specified relative to the workdir.")

    log_file : Path = field(
        default=Path("log.json"),
        kw_only=True,
    )
    """
    The file in the workdir (and eventually in the results archive) that stores
    logs.
    """

    init_exclude_patterns : List[str] = field(
        kw_only=True,
    )
    """
    Patterns to exclude from workspace initialization.
    """

    @init_exclude_patterns.default
    def _init_exclude_pats_def(self):
        return [".git"]

    result_exclude_patterns : List[str] = field(
        kw_only=True,
    )
    """
    Patterns to exclude from workspace result archive.
    """

    @result_exclude_patterns.default
    def _result_exclude_pats_def(self):
        return [".git"]

    old_work_dir : Optional[Path] = field(
        default=None,
        init=False,
    )
    """
    The working directory before the start of the session, to be restored
    after the session.
    """

    start_time : datetime = field(
        factory=datetime.now,
        init=False,
    )
    """
    The time when the session object was created/started.
    """

    def log_exception(self,
                      *excs,
                      exc_type=None,
                      exc_val=None,
                      exc_tb=None,
                      show_locals=True):
        """
        Adds the provided exception to the metadata of this session.
        Useful for detecting errors during the run.

        Arguments:
          *exc: list of exceptions to process, mutually exclusive with
            following args.
          exc_type: The type of the exception.
          exc_val: The value of the exception.
          exc_tb: The traceback of the exception.
          show_locals: should we try to print out information about local
            variables as we parse the exception? (Default: True)
        """

        log.info(
            "Logging exception.",
            workspace=self.number,
            ref=str(self.reference_dir),
            src=str(self.work_dir),
            excs=excs,
            exc_type=exc_type,
            exc_val=exc_val,
            exc_tb=exc_tb,
        )

        exc_data = contextualize_exception(
            *excs,
            exc_type=exc_type,
            exc_val=exc_val,
            exc_tb=exc_tb,
            show_locals=show_locals,
        )

        exception_data = dict(
            time = datetime.now().isoformat(),
            stack = exc_data,
        )

        if 'exceptions' not in self.metadata:
            self.metadata['exceptions'] = list()

        self.metadata['exceptions'].append(exception_data)

    def to_workpath(self,
                      path : Union[str,Path],
                      cwd : Union[None,str,Path] = None):
        """
        Makes sure the input path is an absolute path object with the cwd
        as root.

        Arguments:
          path: The path to normalize
          cwd: The working dir to normalize relative to. (Default: self.workdir)
        """
        if cwd == None:
            cwd = self.work_dir.resolve()

        cwd = Path(cwd)
        if not cwd.is_absolute():
            cwd = self.work_dir / cwd

        path = Path(path)
        if not path.is_absolute():
            path = cwd / path
        return path.resolve()

    @session_op
    def run(self,
            *vargs,
            cwd : Union[str,Path] = None,
            **kwargs) -> subprocess.CompletedProcess:
        """
        Identical to subprocess.run except the working directory is set
        automatically to the workspace directory.
        """

        cwd = self.to_workpath(cwd)

        log.info(
            "Running console command in session.",
            workspace=self.number,
            args=vargs,
            cwd=str(cwd),
            **kwargs
        )

        return subprocess.run(*vargs, cwd=cwd, **kwargs)

    @session_op
    def reset_workspace(self,
                        progress : bool = True,
                        verbose : bool = False,
                        quiet : bool = False):
        """
        Resets the workspace from the reference_workspace, using rsync to
        ensure the files are in an identical state.

        Arguments:
           progress: show a progress bar.
           verbose: rsync verbose output.
           quiet: perform the copy silently.
        """

        # In change number of workspaces changes w/o reference workspace being
        # regenerated.
        self.work_dir.mkdir(parents=True, exist_ok=True)

        rsync_args = dict(
            src=self.reference_dir,
            dst=self.work_dir,
            exclude=self.init_exclude_patterns,
            delete=True,
            update=False,
            progress=progress,
            verbose=verbose,
            quiet=quiet,
        )

        log.info(
            "Resetting workspace with rsync.",
            workspace=self.number,
            **rsync_args,
        )

        Rsync.copy_dir(**rsync_args)

    @session_op
    def enter_workdir(self):
        """
        Changes the current working dir of the session to the workspace.
        """
        if self.old_work_dir != None:
            raise RuntimeError(
                "Trying to enter session directory when already in session directory.")

        self.old_work_dir = Path.cwd().resolve()

        log.info(
            "Entering workdir within session.",
            workspace=self.number,
            old_cwd=str(self.old_work_dir),
            new_cwd=str(self.work_dir),
        )

        os.chdir(self.work_dir)

    @session_op
    def exit_workdir(self):
        """
        Reset the work directory to what it was before enter_workdir.
        """

        if self.old_work_dir == None:
            raise RuntimeError(
                "Trying to exist session dir without first entering")

        log.info(
            "Exiting workdir within session.",
            workspace=self.number,
            old_cwd=str(self.work_dir),
            new_cwd=str(self.old_work_dir),
        )

        os.chdir(self.old_work_dir)
        self.old_work_dir = None

    @session_op
    def session_info(self) -> Dict:
        """
        Returns a number of session specific metadata fields that are then
        added to the metadata file by write_metadata.
        """

        info = dict()

        info['name'] = self.name
        info['start_time'] = self.start_time.isoformat()
        info['end_time'] = datetime.now().isoformat()
        info['reference_dir'] = str(self.reference_dir)
        info['workspace_num'] = self.number
        info['workspace'] = str(self.work_dir)
        info['platform']= platform.system()
        info['platform_release']=platform.release()
        info['platform_version']=platform.version()
        info['architecture']=platform.machine()
        info['hostname']=socket.gethostname()
        info['ip_address']=socket.gethostbyname(socket.gethostname())
        info['mac_address']=':'.join(re.findall('..', '%012x' % uuid.getnode()))
        info['processor']=platform.processor()

        # Get information about the current state of the source repo
        # producing this. This is a best effort thing I don't want to debug so
        # it just moves on if there's errors.
        try:
            src_dir = Path(__file__).resolve().parent
            git_repo = Git.get_repo_root(src_dir)
            if git_repo:
                info['git_repo'] = str(git_repo)
                info['git_refspec'] = Git.get_refspec(src_dir)
                git_branch = Git.get_branch_name(src_dir)
                if git_branch:
                    info['git_branch'] = git_branch
        except:
            pass

        return info

    @session_op
    def write_metadata(self):
        """
        Writes the current metadata to a file in the working directory.
        """

        self.metadata['session_info'] = self.session_info()

        # If this is run in an actor add a message info component.
        message_info = message_metadata()
        if message_info:
            self.metadata['message_info'] = message_info

        meta_path = self.work_dir / self.metadata_file

        log.info(
            "Writing session metadata to file.",
            metadata_file=str(meta_path),
            metadata=self.metadata,
        )

        with meta_path.open('w') as out_file:
            json.dump(self.metadata, out_file, indent="  ")

    @session_op
    def generate_result_archive_files(self):
        """
        Overloadable function to generate a mapping between filesystem files
        and their positions in the results archive.

        The default implementation will compare the reference workspace to the
        current workspace, and produce the list of all changes.

        Note: This is only called by generate_result_archive and will be
        ignored if that function is overridden.

        Returns:
          A `Dict[Union[str,Path],Union[str,Path]]` whose keys are the
          system files to be put into the result archive and whose values
          are the location in the archive each system file goes.
        """

        src = self.work_dir

        rsync_args = dict(
            ref=str(self.reference_dir),
            src=str(src),
            exclude=self.result_exclude_patterns,
        )

        log.info(
            "Finding list of changed files for session's result archive.",
            workspace=self.number,
            **rsync_args,
        )

        changes = Rsync.list_changes(**rsync_args)

        return backup.archive_file_list_to_file_mapping(src,changes)

    @session_op
    def generate_result_archive(self):
        """
        Creates the result archive from the current working directory as it
        is.

        Calls the `generate_result_archive_files` function to get the list,
        which might be overloaded from the default "get changes from reference"
        behavior.
        """

        files = self.generate_result_archive_files()
        out = self.result_archive

        log.info(
            "Generating result archive for session.",
            workspace=self.number,
            ref=str(self.reference_dir),
            src=str(self.work_dir),
            out=str(out),
            files={str(s_f): str(a_f) for s_f, a_f in files.items()},
        )

        backup.archive_file_mapping(files, out, cwd=self.work_dir)

    @session_op
    def validate_complete(self):
        """
        Runs any checks we need to ensure that we can close down the session.
        """

        log.info(
            "Running session close validation checks.",
            workspace=self.number,
        )

        if self.old_work_dir != None:
            raise RuntimeError("Still in work_dir on closing.")
