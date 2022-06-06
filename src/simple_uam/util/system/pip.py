import shutil
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Union, List, Optional
from zipfile import ZipFile
import subprocess
import tempfile
import textwrap
import shutil
from urllib.parse import urlparse
import re
from typing import Optional, Union

from .backup import archive_files
from ..logging import get_logger

log = get_logger(__name__)

class Pip():
    """
    Static class used to wrap a bunch of pip commands.
    """

    @staticmethod
    def install():
        """
        Central function that will run a git init/update operation.
        """

        pass
