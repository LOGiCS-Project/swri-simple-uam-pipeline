from simple_uam.util.config import Config, FDMCompileConfig
from simple_uam.workspace.manager import WorkspaceManager
from simple_uam.craidl.corpus import get_corpus
from simple_uam.util.logging import get_logger
from simple_uam.util.system import Git, Rsync, configure_file, backup_file
from simple_uam.util.system.windows import unpack_file, run_gui_exe
from simple_uam.fdm.compile.build_ops import run_autoreconf, run_configure
from attrs import define, frozen, field
import tempfile
import subprocess
from typing import Optional
import shutil
from pathlib import Path

log = get_logger(__name__)

@frozen
class FDMCompileManager(WorkspaceManager):
    """
    A workspace manager specialized to the Direct2Cad workflow.
    """

    config : FDMCompileConfig = field(
        default = Config[FDMCompileConfig],
        init = False,
    )

    def init_ref_dir(self,
                     reference_dir : Path,
                     assets_dir : Path,
                     fdm_src_repo : Path):
        """
        This function should be overloaded by a child class with a task
        specific setup operation.

        Sets up the reference directory that workspaces are copied from.
        Should only be called by the appropriate task which downloads
        the direct2cad repo and creoson serverl.

        Arguments:
          reference_dir: The reference directory
          assets_dir: The static assets directory
          fdm_src_repo: The FDM source repo
        """

        rsync_args = dict(
            src=str(fdm_src_repo),
            dst=str(reference_dir),
            exclude=['.git'],
            exclude_from=[],
            delete=True,
            update=False,
            progress=True,
        )

        log.info(
            "Copying FDM source repo into FDM build reference directory.",
            **rsync_args,
        )
        Rsync.copy_dir(**rsync_args)


        d2u_globs = Config[FDMCompileConfig].dos2unix_files
        d2u_files = [f for g in d2u_globs for f in reference_dir.glob(g)]
        run_cmd = ['dos2unix.exe',*d2u_files]
        run_args = dict(
            cwd=reference_dir,
        )

        log.info(
            "Iterating over files in the reference workspace with d0s2unix.",
            globs=d2u_globs,
            files=[str(f) for f in d2u_files],
        )

        subprocess.run(
            run_cmd,
            **run_args,
        )

        autoreconf_args = dict(
            cwd=str(reference_dir),
            log_dir=str(reference_dir),
            timeout=self.config.autoreconf_timeout,
        )

        log.info(
            "Running autoreconf in FDM build reference directory.",
            **autoreconf_args,
        )
        m4_dir = reference_dir / 'm4'
        m4_dir.mkdir(parents=True, exist_ok=True)
        run_autoreconf(**autoreconf_args)


        configure_args = dict(
            cwd=str(reference_dir),
            log_dir=str(reference_dir),
            timeout=self.config.configure_timeout,
        )

        log.info(
            "Running configure in FDM build reference directory.",
            **configure_args,
        )
        run_configure(**configure_args)

        log.info(
            "Finished setting up FDM Build reference directory.",
            reference_dir=str(reference_dir),
        )
