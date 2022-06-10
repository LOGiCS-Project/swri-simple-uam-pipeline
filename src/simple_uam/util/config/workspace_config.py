from attrs import define, field
from typing import List
from pathlib import Path

@define
class RecordsConfig():
    """
    Dataclass for options concerning the generation of transaction records.
    """

    max_count : int = -1
    """
    Number of transactio records to save, with the oldest deleted first.
    Negative values mean transactions will never be deleted.
    Zero means that transactions won't be saved at all
    (and produced only lazily)
    """

    min_staletime : int = 60 * 60 # 1hr in seconds
    """
    Number of seconds to keep a transaction record after its last access.
    Lots of non-stale records can lead to keeping more than max_count.
    """

    metadata_file : str = "metadata.json"
    """
    The file within each record that stores metadata.
    """

    log_file : str = "log.json"
    """
    The file which stores log information.
    """

@define
class WorkspaceConfig():

    workspaces_dir : str = field()
    """ Directory containing all the workspaces """

    workspace_subdir_pattern : str = "workspace_{}"
    """
    The pattern for the subdirectory for each individual  workspace, the {}
    will be replaced by a number.
    """

    reference_subdir : str = "reference_workspace"
    """
    The subdirectory which contains the reference, unmodified copy of the
    workspace.
    """

    assets_subdir : str = "assets"
    """
    The subdirectory which contains various static files for use in the
    workspace, usually by symlinking.
    """

    locks_subdir : str = "workspace_locks"
    """ Subdir of workspaces_dir where the various lockfiles are kept. """

    records_subdir : str = "records"
    """ Subdir of workspaces_dir for cached transaction records. """

    records : RecordsConfig = RecordsConfig()
    """ Options concerning records. """

    max_workspaces : int = 4
    """ The maximum number of workspaces operating simultaneously """

    exclude : List[str] = ['.git']
    """
    File patterns to not copy from the reference dir to each workspace.
    Effectively specified relative to the reference dir.

    See rsync's '--exclude' argument for more info.
    """

    exclude_from : List[str] = ['.gitignore']
    """
    Files to extract exclude patterns from for workspace initialization.
    Relative paths are taken to be in the reference directory.

    See rsync's '--exclude-from' argument for more info.
    """

    record_exclude : List[str] = ['.git']
    """
    File patterns to not include in a session's record archive.
    Effectively specified relative to the current workspace dir, as such all
    patterns should be relative.

    See rsync's '--exclude' argument for more info.
    """

    record_exclude_from : List[str] = ['.gitignore']
    """
    Files to extract exclude patterns from when creating a session's record
    archive. All the patterns in a file should be relative.

    Relative paths are taken to be files in the reference directory, not the
    corresponding workspace.

    See rsync's '--exclude-from' argument for more info.
    """

    @property
    def workspaces_path(self):
        """ Path form of Workspaces_dir. """
        return Path(self.workspaces_dir).resolve()

    @property
    def locks_path(self):
        """ Absolute form of lockfile directory. """

        if Path(self.locks_subdir).is_absolute():
            return Path(self.locks_subdir).resolve()
        else:
            return Path(self.workspaces_path / self.locks_subdir).resolve()

    @property
    def reference_path(self):
        """ Absolute form of reference workspace directory. """

        if Path(self.reference_subdir).is_absolute():
            return Path(self.reference_subdir).resolve()
        else:
            return Path(self.workspaces_path / self.reference_subdir).resolve()

    @property
    def reference_lockfile(self):
        """ The lockfile for the reference directory. """

        return self.locks_path / "reference.lock"

    @property
    def assets_path(self):
        """
        Absolute form of workspace asset directory.

        Note: The asset subdir should share the reference lock.
        """

        if Path(self.assets_subdir).is_absolute():
            return Path(self.assets_subdir).resolve()
        else:
            return Path(self.workspaces_path / self.assets_subdir).resolve()

    @property
    def records_path(self):
        """ Absolute form of records directory. """

        if Path(self.records_subdir).is_absolute():
            return Path(self.records_subdir).resolve()
        else:
            return Path(self.workspaces_path / self.records_subdir).resolve()

    @property
    def records_lockdir(self):
        """
        The lockfile for the reference directory.

        Unlike the other lockfiles this is kept in the records directory.
        This allows multiple computers to share a records dir by,
        for instance, keeping it on a shared drive.
        """

        return self.records_path / 'locks'

    @property
    def records_lockfile(self):
        """ The lockfile for the reference directory. """

        return self.records_lockdir / "records.lock"

    def validate_workspace_subdir_num(self, num : int):
        """ Validate whether a particular worker subdir can exist. """

        if num < 0:
            err = RuntimeError(f"Workspace number {num} too low.")
            log.exception(
                "Workspace num must be 1 or greater.",
                num = num,
                err = err,
            )
            raise err
        elif num >= self.max_workspaces:
            err = RuntimeError(f"Workspace number {num} too high.")
            log.exception(
                "Workspace num higher than max_workspaces",
                max_workspaces = Config[UAMWorkspaceConfig].max_workspaces,
                num = num,
                err = err,
            )
            raise err

    def workspace_subdir(self, num : int) -> str:
        """ Get the subdir name for a particular workspace. """

        self.validate_workspace_subdir_num(num)
        return self.workspace_subdir_pattern.format(num)

    def workspace_path(self, num : int) -> Path:
        """ Get the full dirpath for a particular workspace. """

        return (self.workspaces_path / self.workspace_subdir(num)).resolve()

    def workspace_lockfile(self, num : int) -> Path:
        """ Get the lockfile for a particular workspace. """

        return self.locks_path / f"{self.workspace_subdir(num)}.lock"

    @property
    def workspace_nums(self) -> List[int]:
        """ List of all workspace numbers. """

        return range(0,self.max_workspaces)

    @property
    def workspace_subdirs(self) -> List[str]:
        """ List of all workspace subdir names. """

        return [self.workspace_subdir(n) for n in self.workspace_nums]

    @property
    def workspace_paths(self) -> List[Path]:
        """ List of all workspace dirs. """
        return [self.workspace_path(n) for n in self.workspace_nums]

    @property
    def workspace_lockfiles(self) -> List[Path]:
        """ List of all workspace lockfiles.
        """
        return [self.workspace_lockfile(n) for n in self.workspace_nums]

    @property
    def exclude_from_paths(self):
        """
        self.exclude_from with all absolute Paths.
        """
        paths = list()
        for f in self.exclude_from:
            f = Path(f)
            if not f.is_absolute():
                f = self.reference_path / f
            paths.append(f)
        return paths

    @property
    def record_exclude_from_paths(self):
        """
        self.exclude_from with all absolute Paths.
        """
        paths = list()
        for f in self.exclude_from:
            f = Path(f)
            if not f.is_absolute():
                f = self.reference_path / f
            paths.append(f)
        return paths
