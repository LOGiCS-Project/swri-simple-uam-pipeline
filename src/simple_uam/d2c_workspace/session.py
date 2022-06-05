from simple_uam.workspace.session import Session
from simple_uam.util.logging import get_logger

log = get_logger(__name__)

@define
class D2CSession(Session):
    """
    A workspace session specialized to the direct2cad workflow.
    """
    pass
