# from typing import List, Tuple, Optional, Union
# from pathlib import Path
# from util.invoke import task
# from attrs import define, frozen, field
# from filelock import Timeout, FileLock
# import shutil
# import tempfile
# import subprocess
# import random
# import string
# from datetime import datetime
# import heapq

from util.config import Config
from ..generic.config import RecordsConfig
from ..generic.manager import WorkspaceManager
from ..config import UAMWorkspaceConfig
from util.logging import get_logger

log = get_logger(__name__)

@frozen
class Direct2CadManager(WorkspaceManager):
    """
    A workspace manager specialized to the Direct2Cad workflow.
    """

    config : UAMWorkspaceConfig = field(
        default = Config[UAMWorkspaceConfig],
        init = False,
    )

    def initialize_reference(self):
        """
        Copies files over from direct2cad submodule.
        """

        raise NotImplementedError()
