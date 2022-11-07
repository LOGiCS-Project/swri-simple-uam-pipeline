
from attrs import define, field, frozen, setters
from typing import List, Tuple, Dict, Optional, Union, Type

from simple_uam.util.config import Config, FDMCompileConfig
from simple_uam.util.logging import get_logger

from simple_uam.workspace import Workspace

from pathlib import Path
from .manager import FDMCompileManager
from .session import FDMCompileSession

log = get_logger(__name__)

@define
class FDMCompileWorkspace(Workspace):
    """
    A temporary wrapper that represents a FDM Build workspace w/ possibly
    an ongoing session transaction.

    Mostly the same as Workspace except that it hardcodes in the manager and
    session_class.
    """

    manager : FDMCompileManager = field(
        factory=FDMCompileManager,
        on_setattr=setters.frozen,
        init=False,
    )

    config : FDMCompileConfig = field(
        init=False,
        on_setattr=setters.frozen,
    )
    """ The workspace config object that collects all the relevant paths. """

    @config.default
    def _config_def(self):
        return self.manager.config

    session_class : Type[FDMCompileSession] = field(
        default=FDMCompileSession,
        init=False,
        on_setattr=setters.frozen,
    )
    """
    The class we're using to generate the active session context.
    """

    active_session : Optional[FDMCompileSession] = field(
        default=None,
        init=False,
    )
    """
    The current session context. Should be non-None after
    session_started.
    """

    copy_bins : List[Union[str, Path]] = field(
        factory=list,
        kw_only=True,
    )
    """
    Do we copy the binaries generated from this session into some location?
    If so where?
    """

    copy_zips :  List[Union[str, Path]] = field(
        factory=list,
        kw_only=True,
    )
    """
    Do we copy the output archives from this session into some locations?
    if so where?
    """

    def extra_session_params(self):
        """
        Passes bins and zip params to the newly created session.
        """

        return dict(
            copy_bins = self.copy_bins,
            copy_zips = self.copy_zips,
        )
