
from simple_uam.workspace.session import Session, session_op
from simple_uam.util.logging import get_logger
from attrs import define,field

log = get_logger(__name__)

@define
class D2CSession(Session):
    """
    A workspace session specialized to the direct2cad workflow.
    """

    @session_op
    def build_cad(self, design):
        """
        Runs buildcad.py on a particular design, lavning changes and parsed
        results in place for session cleanup to manage.
        """
        pass
