from .config import RecordsConfig, WorkspaceConfig
from typing import List, Tuple, Optional, Union
from pathlib import Path
from util.logging import get_logger
from util.invoke import task
from attrs import define, frozen, field
from filelock import Timeout, FileLock
import shutil
import tempfile
import subprocess
import random
import string
from datetime import datetime
import heapq

log = get_logger(__name__)

@frozen
class WorkspaceManager():
    """
    Object that provides locks for a particular workspace and holds some
    abstract functions for initializing the reference workspace.
    """

    config : WorkspaceConfig = field()
    """ The workspace config object that collects all the relevant paths. """

    def reference_lock(self) -> FileLock:
        """
        Lockfile for reference directory.

        Note: We provide new locks on every request due to reentrancy issues.
              Multiple threads sharing the same lock isn't the behavior we want.
        """

        return FileLock(self.config.reference_lockfile)

    def records_lock(self) -> FileLock:
        """
        Lockfile for the records storage directory.

        Note: We provide new locks on every request due to reentrancy issues.
              Multiple threads sharing the same lock isn't the behavior we want.
        """
        return FileLock(self.config.records_lockfile)

    def workspace_lock(self, num : int) -> FileLock:
        """
        Lockfile for single workspace directory.

        Note: We provide new locks on every request due to reentrancy issues.
              Multiple threads sharing the same lock isn't the behavior we want.
        """
        return FileLock(self.config.workspace_lockfile(num))

    def acquire_workspace_lock(self, num : Optional[int] = None
    ) -> Optional[Tuple[int,FileLock]]:
        """
        Will attempt to acquire a lock for a specific workspace, returns None
        on failure.

        If successful will return a tuple of workspace number and ALREADY
        ACQUIRED lock. The caller MUST ensure that the lock is released.
        """

        workspace_queue = [num]
        if num == None:
            workspace_queue = self.config.workspace_nums

        for workspace_num in workspace_queue:
            lock = self.workspace_lock(workspace_num)
            try:
                lock.acquire(blocking=False)
                return tuple(workspace_num,lock)
            except Timeout:
                # Will only fail in lock.acquire and that cleans up after itself.
                pass

        # No lock free
        return None

    def init_dirs(self):
        """
        Creates the various workspace directories and subdirs that this class
        manages.
        """

        managed_dirs = [
            self.config.workspaces_path,
            self.config.locks_path,
            self.config.reference_path,
            self.config.records_path,
            self.config.records_lockdir,
            *self.config.workspace_paths,
        ]

        for d in managed_dirs:
            d.mkdir(parents=True, exist_ok=True)

    def add_record(self,
                   archive : Union[str,Path],
                   prefix : Optional[str] = None,
                   suffix : Optional[str] = None,
                   copy : bool = True,
    ) -> Optional[Path]:
        """
        Adds an archive to the record directory.

        Arguments:
           archive: The file to be moved into the record dir.
           prefix: The prefix to the final file name.
           suffix: The file extension to use.
           copy: copy the file if true, otherwise move.

        Returns:
           The path to the resulting file in records dir, none if
           no record was saved.
        """

        # No records to save, don't bother.
        if Config[UAMWorkspaceConfig].max_record_count == 0:
            return None

        # Normalize and validate input
        archive = Path(archive)

        if not archive.exists() or not archive.is_file():
            raise RuntimeError(f"Expected {archive} to be file, cannot proceed.")

        # Get archive file name setup
        time_str = datetime.now().strftime("%Y-%m-%d")
        uniq_str = ''.join(random.choices(
            string.ascii_lowercase + string.digits, k=10))

        if not prefix:
            prefix = archive.stem

        if not suffix:
            suffix = archive.suffix

        if not suffix.startswith('.'):
            suffix = "." + suffix

        out_file = f"{prefix}-{time_str}-{uniq_str}{suffix}"

        with tempfile.TemporaryDirectory() as tmp_dir:

            # Create a temorary copy if needed.
            if copy:
                target = Path(tmp_dir) / out_file
                shutil.copy2(archive, target)
                archive = target

            # Move temp_file to records dir (no lock needed)
            out_path = self.config.records_path / out_file
            shutil.move(archive, out_path)

            # Return the resulting filepath
            return out_path

    def prune_records(cls):
        """
        Deletes the oldest files in the records dir if there are too many.
        """

        # Never pruning records, don't bother.
        if Config[UAMWorkspaceConfig].max_record_count < 0:
            return

        # Gather records that are old enough to prune.
        now = datetime.now()
        records = list()
        total_records = 0
        for record in self.config.records_path.iterdir():
            if record.is_file():
                total_records += 1
                access_time = datime.from_timestamp(record.stat().st_atime)
                staletime = (now - access_time).total_seconds()
                if staletime > self.config.records.min_staletime:
                    records.append(tuple(staletime,record))

        # Short circuit if there's nothing to prune
        surplus_records = total_records - self.config.records.max_count
        if surplus_records <= 0:
            return

        # Gather the oldest.
        records = heapq.nlargest(
            surplus_records,
            records,
            key=lambda t: t[0],
        )

        try:
            # Presumably someone else is also pruning if there's a lock,
            # Just let them do the work, and move on.
            with self.records_lock().acquire(blocking=False):
                for record in records:
                    # If a record got deleted before this point, that's fine.
                    records.unlink(missing_ok=True)
        except Timeout:
            pass

    def initialize_reference(self):
        """
        This function should be overloaded by a child class with a task
        specific setup operation.

        Sets up the reference directory that workspaces are copied from.
        Should ensure that it acquires a lock on the reference directory
        beforehand.
        """

        raise NotImplementedError("Overload in child class. See docstring.")