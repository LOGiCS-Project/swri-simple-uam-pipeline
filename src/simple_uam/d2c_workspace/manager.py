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
    def init_ref_dir(self):
        """
        Copies files over from direct2cad submodule.
        """

        # Copy over direct2cad workspace
        # Extract the creoson server archive
        # Rename the creoson server dir to 'creoson-server'
        # change the version of creo in 'parametric.bat" from '6.0.4.0' to '5.0.6.0'
        raise NotImplementedError()
