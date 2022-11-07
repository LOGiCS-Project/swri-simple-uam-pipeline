from simple_uam.util.config import Config, FDMEvalConfig
from simple_uam.workspace.manager import WorkspaceManager
from simple_uam.craidl.corpus import get_corpus
from simple_uam.util.logging import get_logger
from simple_uam.util.system import Git, Rsync, configure_file, backup_file
from simple_uam.util.system.windows import unpack_file, run_gui_exe
from attrs import define, frozen, field
import tempfile
import subprocess
from typing import Optional
import shutil
from pathlib import Path

log = get_logger(__name__)

@frozen
class FDMEvalManager(WorkspaceManager):
    """
    A workspace manager specialized to the Direct2Cad workflow.
    """

    config : FDMEvalConfig = field(
        default = Config[FDMEvalConfig],
        init = False,
    )

    def init_ref_dir(self,
                     reference_dir : Path,
                     assets_dir : Path,
                     fdm_env_repo : Path):
        """
        This function should be overloaded by a child class with a task
        specific setup operation.

        Sets up the reference directory that workspaces are copied from.
        Should only be called by the appropriate task which downloads
        the direct2cad repo and creoson serverl.

        Arguments:
          reference_dir: The reference directory
          assets_dir: The static assets directory
          fdm_env_repo: The FDM environment repo
        """

        # Copy over environment details
        rsync_args = dict(
            src=str(fdm_env_repo),
            dst=str(reference_dir),
            exclude=['.git'],
            exclude_from=[],
            delete=True,
            update=False,
            progress=True,
        )

        log.info(
            "Copying FDM environment repo into FDM eval reference directory.",
            **rsync_args,
        )
        Rsync.copy_dir(**rsync_args)
