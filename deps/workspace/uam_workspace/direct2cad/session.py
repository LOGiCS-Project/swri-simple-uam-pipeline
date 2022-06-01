
from util.config import Config
from ..generic.config import RecordsConfig
from ..generic.manager import WorkspaceManager
from ..generic.session import Session, session_op
from ..config import UAMWorkspaceConfig
from .manager import Direct2CadManager
from util.logging import get_logger

log = get_logger(__name__)

@define
class Direct2CadSession(Session):
    """
    A workspace session specialized to the direct2cad workflow.
    """
    pass
