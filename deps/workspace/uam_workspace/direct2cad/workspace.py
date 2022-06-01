
from util.config import Config
from ..generic.config import RecordsConfig
from ..generic.manager import WorkspaceManager
from ..generic.session import Session, session_op
from ..generic.workspace import Workspace
from ..config import UAMWorkspaceConfig
from .manager import Direct2CadManager
from .session import Direct2CadWorkspace
from util.logging import get_logger

log = get_logger(__name__)

@define
class Direct2CadWorkspace(Workspace):
    """
    A temporary wrapper that represents a direct2cad workspace w/ possibly
    an ongoing session transaction.

    Mostly the same as Workspace except that it hardcodes in the manager and
    session_class.
    """

    manager : Direct2CadManager = field(
        factory=Direct2CadManager,
        frozen=True,
        init=False,
    )

    config : UAMWorkspaceConfig = field(
        init=False,
        frozen=True,
    )
    """ The workspace config object that collects all the relevant paths. """

    @config.default
    def _config_def(self):
        return self.manager.config

    session_class : Type[Session] = field(
        default=Direct2CadSession,
        init=False,
        frozen=True,
    )
    """
    The class we're using to generate the active session context.
    """

    active_session : Optional[Direct2CadSession] = field(
        default=None,
        init=False,
    )
    """
    The current session context. Should be non-None after
    session_started.
    """
