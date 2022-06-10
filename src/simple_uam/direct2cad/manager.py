from simple_uam.util.config import Config, D2CWorkspaceConfig
from simple_uam.workspace.manager import WorkspaceManager
from simple_uam.util.logging import get_logger

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

    @staticmethod
    def init_ref_dir(reference_dir : Path,
                     assets_dir : Path,
                     direct2cad_repo : Path,
                     creoson_server_zip : Path):
        """
        This function should be overloaded by a child class with a task
        specific setup operation.

        Sets up the reference directory that workspaces are copied from.
        Should only be called by
        """

        # copy direct2cad files into ref_dir
        # unpack creoson_server into ref_dir

        raise NotImplementedError("Overload in child class. See docstring.")
