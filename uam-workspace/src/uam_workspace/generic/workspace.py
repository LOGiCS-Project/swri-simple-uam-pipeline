
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
from copy import deepcopy
import tempfile
import random
import string
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

    name : str = field(
        default="generic-session",
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

    Can be set at init, or modified before session start. Changes to this
    persist between sessions.
    """

    session_class : Type[Session] = field(
        default=Session,
        kw_only=True,
        frozen=True,
    )
    """
    The class we're using to generate the active session context.
    """

    active_session : Optional[Session] = field(
        default=None,
        init=False,
    )
    """
    The current session context. Should be non-None after
    session_started.
    """

    active_workspace : Optional[int] = field(
        default=None,
        init=False,
    )
    """
    The current active workspace within a session.
    """

    active_lock : Optional[FileLock] = field(
        default=None,
        init=False,
    )
    """ The FileLock for the current workspace. """


    active_temp_dir : Optional[tempfile.TemporaryDirectory] = field(
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
        if self.active_session:
            raise RuntimeError(
                "Workspace currently in session, can't start a new one.")

        # Get lock if possible, fail otherwise.
        lock_tuple = self.manager.acquire_workspace_lock(self.number)
        if lock_tuple == None:
            raise RuntimeError("Could not acquire Workspace lock.")
        try:
            # mark session_start
            self.record_archive = None
            self.active_workspace = lock_tuple[0]
            self.active_lock = lock_tuple[1]

            # create temp_dir & temp_records dir name
            self.active_temp_dir = tempfile.TemporaryDirectory()
            uniq_str = ''.join(random.choices(
                string.ascii_lowercase + string.digits, k=10))
            temp_archive = Path(self.active_temp_dir.name) / f"{self.name}-{uniq_str}.zip"

            # setup metadata
            metadata = deepcopy(self.metadata)

            # create active session
            self.active_session = self.session_class(
                reference_dir=self.config.reference_path,
                work_dir=self.config.workspace_path(self.active_workspace),
                result_archive=temp_archive,
                metadata=metadata,
                name=self.name,
                metadata_file=self.config.records.metadata_file,
            )
            self.active_session.reset_workspace(
                progress=False,
            )

            pass
        except Exception:
            # Perform Cleanup
            if self.active_temp_dir:
                self.active_temp_dir.cleanup()
            if lock_tuple:
                lock_tuple[1].release()

            # Reset Internal State
            self.active_session = None
            self.active_workspace = None
            self.active_lock = None
            self.active_temp_dir = None
            self.record_archive = None

            # Re-raise exception
            raise

    def finish(self):
        """
        Finishes an active session.
        """
        if not self.active_session:
            raise RuntimeError("Trying to finish session without an active session.")
        try:

            if self.config.records.max_count != 0:
                # Generate the records archive
                self.active_session.write_metadata()
                self.active_session.generate_record_archive()

                # Move it to the manager's records directory
                self.record_archive = self.manager.add_record(
                    archive=self.active_session.result_archive,
                    prefix=self.name,
                    copy=False,
                )

            # Ensure we can close session
            self.active_session.validate_complete()

        finally:
            # release lock
            self.active_lock.release()
            self.active_temp_dir.cleanup()

            # reset workspace state
            self.active_session = None
            self.active_workspace = None
            self.active_lock = None
            self.active_temp_dir = None

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
