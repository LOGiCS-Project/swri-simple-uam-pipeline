from simple_uam.util.config import Config, D2CWorkspaceConfig
from simple_uam.workspace.manager import WorkspaceManager
from simple_uam.craidl.corpus import get_corpus
from simple_uam.util.logging import get_logger
from simple_uam.util.system import Git, Rsync, configure_file, backup_file
from simple_uam.util.system.windows import unpack_file, run_gui_exe
from attrs import define, frozen, field
import tempfile
from typing import Optional
import shutil
from pathlib import Path

log = get_logger(__name__)

@frozen
class D2CManager(WorkspaceManager):
    """
    A workspace manager specialized to the Direct2Cad workflow.
    """

    config : D2CWorkspaceConfig = field(
        default = Config[D2CWorkspaceConfig],
        init = False,
    )

    creoson_server_subdir : str = field(
        default="creoson-server",
        init=False,
    )

    creoson_unpack_folder : str = field(
        default="CreosonServerWithSetup-2.8.0-win64",
        init=False,
    )

    creoson_setup_exe : str = field(
        default="CreosonSetup.exe",
        init=False,
    )

    def init_ref_dir(self,
                     reference_dir : Path,
                     assets_dir : Path,
                     direct2cad_repo : Path,
                     uav_workflows_repo : Path,
                     creoson_server_zip : Path,
                     setvars_file : Optional[Path],
                     copy_uav_parts : Optional[bool] = None):
        """
        This function should be overloaded by a child class with a task
        specific setup operation.

        Sets up the reference directory that workspaces are copied from.
        Should only be called by the appropriate task which downloads
        the direct2cad repo and creoson server.

        Arguments:
          reference_dir: The reference directory
          assets_dir: The static assets directory
          direct2cad_repo: The direct2cad repo
          uav_workflows_repo: The UAV_Workflows repo
          creoson_server_zip: Zip w/ creoson server
          setvars_file: The setvars.bat file to put in the creoson server dir.
            If none will start the creoson server gui.
          copy_uav_parts: Should parts from the UAV Workflows repo be copied
            int the reference directory, overriding any direct2cad parts?
            If none, will use whatever setting is in the config.
        """

        rsync_args = dict(
            src=str(direct2cad_repo),
            dst=str(reference_dir),
            exclude=['.git'],
            exclude_from=[],
            delete=True,
            update=False,
            progress=True,
        )

        log.info(
            "Copying direct2cad repo into reference directory.",
            **rsync_args,
        )
        Rsync.copy_dir(**rsync_args)

        creoson_ref_dir = reference_dir / self.creoson_server_subdir

        log.info(
            "Modifying parametric.bat to reference correct Creo version")

        para_bat = reference_dir / "parametric.bat"

        configure_file(
            para_bat,
            para_bat,
            replacements={"6.0.4.0":"5.0.6.0"},
            backup=True,
            exist_ok=True,
        )

        if creoson_ref_dir.exists():
            log.info(
                "Found existing creoson server dir, deleting.",
                creoson_dir=str(creoson_ref_dir),
            )
            shutil.rmtree(creoson_ref_dir,ignore_errors=True)

        log.info(
            "Unpacking creoson server zip into reference dir.",
            creoson_zip = str(creoson_server_zip),
            creoson_dir = str(creoson_ref_dir),
        )

        creoson_ref_dir.mkdir(parents=True, exist_ok=True)
        unpack_file(creoson_server_zip, creoson_ref_dir)

        setvars_bat = creoson_ref_dir / 'setvars.bat'

        if setvars_file:
            setvars_file = Path(setvars_file)
            log.info(
                "Copying provided setvars.bat into reference dir.",
                input=str(setvars_file),
                output=str(setvars_bat),
            )
            shutil.copy2(setvars_file, setvars_bat)
        else:
            log.info(
                "No setvars.bat provided, running GUI to generate.",
            )
            run_gui_exe(
                creoson_ref_dir / self.creoson_setup_exe,
                notes="""
                ### Setting Up Creoson Server ###

                  - Step 1: Use the Creo 5.0.6.0 Common Files folder

                    > C:\Program Files\PTC\Creo 5.0.6.0\Common Files

                  - Step 2: Don't Change Port (Default: 9056)

                  - Final Step: Start and Stop the server before closing app.
                """,
                wait=True,
            )

        if copy_uav_parts == None:
            copy_uav_parts = Config[D2CWorkspaceConfig].copy_uav_parts

        if copy_uav_parts:
            uav_cad_dir = Path(uav_workflows_repo) / "CAD"
            ref_cad_dir = reference_dir / "CAD"

            log.info(
                "Copying CAD files from UAV workflows repo.",
                uav_cad_dir=str(uav_cad_dir),
                ref_cad_dir=str(ref_cad_dir),
            )

            for uav_cad in uav_cad_dir.iterdir():
                ref_cad = ref_cad_dir / uav_cad.name
                backup_file(ref_cad, delete=True)
                shutil.copy2(uav_cad, ref_cad)
        else:
            log.info(
                "Not copying UAV Workflows CAD files into reference workspace.",
            )
