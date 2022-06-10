
from attrs import define, field, frozen, setters
from typing import List, Tuple, Dict, Optional, Union, Type

from simple_uam.util.config import Config, D2CWorkspaceConfig
from simple_uam.util.logging import get_logger

from simple_uam.workspace import Workspace

from .manager import D2CManager
from .session import D2CSession

log = get_logger(__name__)

@define
class D2CWorkspace(Workspace):
    """
    A temporary wrapper that represents a direct2cad workspace w/ possibly
    an ongoing session transaction.

    Mostly the same as Workspace except that it hardcodes in the manager and
    session_class.
    """

    manager : D2CManager = field(
        factory=D2CManager,
        on_setattr=setters.frozen,
        init=False,
    )

    config : D2CWorkspaceConfig = field(
        init=False,
        on_setattr=setters.frozen,
    )
    """ The workspace config object that collects all the relevant paths. """

    @config.default
    def _config_def(self):
        return self.manager.config

    session_class : Type[D2CSession] = field(
        default=D2CSession,
        init=False,
        on_setattr=setters.frozen,
    )
    """
    The class we're using to generate the active session context.
    """

    active_session : Optional[D2CSession] = field(
        default=None,
        init=False,
    )
    """
    The current session context. Should be non-None after
    session_started.
    """
