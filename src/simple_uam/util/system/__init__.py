from .backup import backup_file, archive_files, configure_file
from .rsync import Rsync
from .git import Git
from .pip import Pip
# We don't import '.windows' so that you have to import platform specific stuff
# manually.

from typing import List

__all__: List[str] = [
    'backup_file',
    'archive_files',
    'configure_file',
    'Rsync',
    'Git',
    'Pip',
]  # noqa: WPS410 (the only __variable__ we use)
