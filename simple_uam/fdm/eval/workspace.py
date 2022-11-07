
from attrs import define, field, frozen, setters
from typing import List, Tuple, Dict, Optional, Union, Type

from simple_uam.util.config import Config, FDMEvalConfig
from simple_uam.util.logging import get_logger

from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic
from pathlib import Path
from simple_uam.workspace import Workspace

from .manager import FDMEvalManager
from .session import FDMEvalSession

log = get_logger(__name__)

@define
class FDMEvalWorkspace(Workspace):
    """
    A temporary wrapper that represents a FDM Build workspace w/ possibly
    an ongoing session transaction.

    Mostly the same as Workspace except that it hardcodes in the manager and
    session_class.
    """

    manager : FDMEvalManager = field(
        factory=FDMEvalManager,
        on_setattr=setters.frozen,
        init=False,
    )

    config : FDMEvalConfig = field(
        init=False,
        on_setattr=setters.frozen,
    )
    """ The workspace config object that collects all the relevant paths. """

    @config.default
    def _config_def(self):
        return self.manager.config

    session_class : Type[FDMEvalSession] = field(
        default=FDMEvalSession,
        init=False,
        on_setattr=setters.frozen,
    )
    """
    The class we're using to generate the active session context.
    """

    active_session : Optional[FDMEvalSession] = field(
        default=None,
        init=False,
    )
    """
    The current session context. Should be non-None after
    session_started.
    """
