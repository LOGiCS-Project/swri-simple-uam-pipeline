
from .config import UAMWorkspaceConfig
from util.config import Config
from .paths import *
from .manager import WorkspaceManager
from typing import List, Tuple, Dict
from pathlib import Path
from util.logging import get_logger
from util.invoke import task
from attrs import define,field
from filelock import Timeout, FileLock
from functools import wraps
from .session import Session
import tempfile
import subprocess

log = get_logger(__name__)

@define
class Workspace():
    """
    A temporary wrapper which represents a single session within a workspace.
    Holds the current lock and some other stuff for the workspace and
    whatever return values ought to be accesible after the workspace has
    closed.

    Acts as a context manager.
    """

    manager : WorkspaceManager = field(
        frozen=True,
    )

    config : WorkspaceConfig = field(
        init=False,
        frozen=True,
    )
    """ The workspace config object that collects all the relevant paths. """

    @config.default
    def _config_def(self):
        return self.manager.config

    name : Optional[str] = field(
        default=None,
    )
    """ A name for the type of session being performed. """

    number : Optional[int] = field(
        default=None,
        kw_only=True,
    )
    """ The number of the workspace this object is operating with. """

    metadata : Dict = field(
        factory=dict,
        kw_only=True,
    )
    """
    The metadata for this session, will be stored in metadata.json in the
    record archive.

    Can be set at init, or modified before session end.
    """

    @property
    def session_ongoing(self):
        return session_started and not session_ended

    session_class : Type[Session] = field(
        default=Session,
        kw_only=True,
        frozen=True,
    )
    """
    The class we're using to generate the active session context.
    """

    session_started : bool = field(
        default=False,
        init=False,
    )
    """
    Has the session started yet?
    If true and not session_ended then we should hold the lock.
    """

    session_ended : bool = field(
        default=False,
        init=False,
    )
    """
    Has the session finished yet?
    Can only be true if session_started. If true, then lock has been released.
    """

    active_session : Optional[Session] = field(
        default=False,
        init=False,
    )
    """
    The current session context. Should be non-None after
    session_started.
    """

    lock : Optional[FileLock] = field(
        default=None,
        init=False,
    )
    """ The FileLock for the current workspace. """


    temp_dir : Optional[tempfile.TemporaryDirectory] = field(
        default=None,
        init=False,
    )
    """
    The temporary directory the record archive is written to before it's
    moved into the records directory.
    """

    record_archive : Optional[Path] = field(
        default=None,
        init=False,
    )
    """
    The path to the record archive file after a session has completed.
    """

    def start(self) -> Session:
        """
        Starts the session, meant to be used in a try-finally style.

        ```
        workspace = Workspace(...)
        session = workspace.start()
        try:
           do_stuff_here()
           session.run(...)
        finally:
           workspace.finish()
        ```

        Note that this won't change the working directory, unlike when a
        workspace is used as a context managed.
        """

        # Checks
        if self.session_ongoing:
            raise RuntimeError(
                "Workspace currently in session, can't start a new one.")

        # Get lock if possible, fail otherwise.
        try:
            # mark session_start
            # create temp_dir & temp_records dir name
            # setup metadata
            # create active session
               # in session: reset workspace

            pass
        finally:
            # release lock and reset internal state
            pass

    def finish(self):
        """
        Finishes an active session.
        """
        try:
            if WRITING_RECORD_ARCHIVE:
                self.active_session.write_metadata()
                self.active_session.generate_record_archive()
                # Copy archive into rrcord dir via manager, save value to return.
        finally:
            # release lock
            # reset workspace state
            # release temp_dir
            # mark session_end
            pass

    def __enter__(self):
        """
        Provides a context manager you can use to do various tasks within the
        Workspace.

        ```
        workspace = Workspace(...)
        with workspace as session:
            # current working directory is now the workspace
            do_stuff_here()
            session.run(...)
        ```
        """
        session = self.start()
        session.enter_workdir()
        return session

    def __exit__(self, exp_typ, exp_val, exp_traceback):
        self.active_session.exist_workdir()
        self.finish()
        return None
