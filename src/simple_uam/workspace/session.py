
from typing import List, Tuple, Dict, Optional, Union
from pathlib import Path
from simple_uam.util.logging import get_logger
from simple_uam.util.system import Rsync
from attrs import define,field
from filelock import Timeout, FileLock
from functools import wraps
from datetime import datetime
from copy import deepcopy
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
    )
    """ The reference directory that the work_dir is copied from. """

    @reference_dir.validator
    def _ref_dir_valid(self, attr, val):
        if not val.is_absolute():
            raise RuntimeError("Session init paths must be absolute.")

    work_dir : Path = field(
        kw_only=True,
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
        if val.exists():
            raise RuntimeError("Result archive cannot already exist.")

    @property
    def result_archive(self):
        return self._result_archive

    @result_archive.setter
    def result_archive(self, val):
        self.metadata['result-archive'] = str(val)
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
    record archive.

    Will be initialized by the Workspace.
    """

    metadata_file : Path = field(
        default=Path("metadata.json"),
        kw_only=True,
    )
    """
    The file in the workdir (and eventually in the records archive) that stores
    the current metadata.
    """

    @metadata_file.validator
    def _meta_file_valid(self, attr, val):
        if val.is_absolute():
            raise RuntimeError("The metadata file must be specified relative to the workdir.")

    init_exclude_patterns : List[str] = field(
        kw_only=True,
    )
    """
    Patterns to exclude from workspace initialization.
    """

    @init_exclude_patterns.default
    def _init_exclude_pats_def(self):
        return [".git"]

    init_exclude_files : List[Path] = field(
        kw_only=True,
    )
    """
    Files to read for exclude lists.
    """

    @init_exclude_files.default
    def _init_exclude_files_def(self):
        e_files = list()
        gitignore = self.reference_dir / ".gitignore"
        if gitignore.exists():
            e_files.append(gitignore)
        return e_files

    @init_exclude_files.validator
    def _init_exclude_files_valid(self, attr, val):
        for e_file in val:
            if not e_file.is_absolute():
                raise RuntimeError("Session init exclude paths must be absolute.")

    record_exclude_patterns : List[str] = field(
        kw_only=True,
    )
    """
    Patterns to exclude from workspace record archive.
    """

    @record_exclude_patterns.default
    def _record_exclude_pats_def(self):
        return [".git"]

    record_exclude_files : List[Path] = field(
        kw_only=True,
    )
    """
    Files to read for record archive exclude lists.
    """

    @record_exclude_files.default
    def _record_exclude_files_def(self):
        e_files = list()
        gitignore = self.reference_dir / ".gitignore"
        if gitignore.exists():
            e_files.append(gitignore)
        return e_files

    @record_exclude_files.validator
    def _record_exclude_files_valid(self, attr, val):
        for e_file in val:
            if not e_file.is_absolute():
                raise RuntimeError("Session record exclude paths must be absolute.")

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

    @session_op
    def run(self,
            *vargs,
            cwd : Union[str,Path] = None,
            **kwargs) -> subprocess.CompletedProcess:
        """
        Identical to subprocess.run except the working directory is set
        automatically to the workspace directory.
        """
        if cwd == None:
            cwd = self.work_dir

        cwd = Path(cwd)
        if not cwd.is_absolute():
            cwd = self.work_dir / cwd

        log.info(
            "Running console command in session.",
            workspace=self.number,
            args=args,
            cwd=str(cwd),
            **kwargs
        )

        return subprocess.run(*args, cwd=cwd, **kwargs)

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

        rsync_args = dict(
            src=self.reference_dir,
            dst=self.work_dir,
            exclude=self.init_exclude_patterns,
            exclude_from=self.init_exclude_files,
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
        info['start-time'] = self.start_time.isoformat()
        info['end-time'] = datetime.now().isoformat()
        info['reference-dir'] = str(self.reference_dir)
        info['workspace-num'] = self.number
        info['workspace'] = str(self.work_dir)
        info['platform']= platform.system()
        info['platform-release']=platform.release()
        info['platform-version']=platform.version()
        info['architecture']=platform.machine()
        info['hostname']=socket.gethostname()
        info['ip-address']=socket.gethostbyname(socket.gethostname())
        info['mac-address']=':'.join(re.findall('..', '%012x' % uuid.getnode()))
        info['processor']=platform.processor()

        return info


    @session_op
    def write_metadata(self):
        """
        Writes the current metadata to a file in the working directory.
        """

        self.metadata['session-info'] = self.session_info()

        meta_path = self.work_dir / self.metadata_file

        log.info(
            "Writing session metadata to file.",
            metadata_file=str(self.meta_path),
            metadata=self.metadata,
        )

        with meta_path.open('w') as out_file:
            json.dump(self.metadata, out_file)

    @session_op
    def generate_record_archive(self):
        """
        Creates the record archive from the current working directory as it
        is.
        """

        rsync_args = dict(
            ref=str(self.reference_dir),
            src=str(self.work_dir),
            out=str(self.result_archive),
            exclude=self.record_exclude_patterns,
            exclude_from=[str(f) for f in self.record_exclude_files],
        )

        log.info(
            "Generating record archive for session.",
            workspace=self.number,
            **rsync_args,
        )

        Rsync.archive_changes(**rsync_args)

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
