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

    def initialize_reference(self):
        """
        Copies files over from direct2cad submodule.
        """

        raise NotImplementedError()
