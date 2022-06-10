from simple_uam.util.config import Config, D2CWorkspaceConfig
from simple_uam.workspace.manager import WorkspaceManager
from simple_uam.craidl.corpus import get_corpus
from simple_uam.util.logging import get_logger
from simple_uam.util.system import Git, Rsync
from simple_uam.util.system.windows import unpack_file
from attrs import define, frozen, field
import tempfile
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

    def init_ref_dir(self,
                     reference_dir : Path,
                     assets_dir : Path,
                     direct2cad_repo : Path,
                     creoson_server_zip : Path):
        """
        This function should be overloaded by a child class with a task
        specific setup operation.

        Sets up the reference directory that workspaces are copied from.
        Should only be called by
        """

        rsync_args = dict(
            src=str(direct2cad_repo),
            dst=str(reference_dir),
            exclude=['.git'],
            exclude_from=[str(direct2cad_repo / '.gitignore')],
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
            "Unpacking creoson server zip into reference dir.",
            creoson_zip = str(creoson_server_zip),
            creoson_dir = str(creoson_ref_dir),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            unpack_file(creoson_server_zip, temp_dir)
            creoson_unpack_dir = Path(temp_dir) / self.creoson_unpack_folder
            shutil.move(creoson_unpack_dir, creoson_ref_dir)
