"""
SimpleUAM windows node setup scripts.
"""

from .actions.actors import gen_info_files, process_design
from typing import List # noqa

__all__: List[str] = [
    'gen_info_files',
    'process_design',
]  # noqa: WPS410 (the only __variable__ we use)
