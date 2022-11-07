"""
SimpleUAM development utilities.
"""

from typing import List # noqa
from . import setup, manage

__all__: List[str] = [
    'setup',
    'manage',
]  # noqa: WPS410 (the only __variable__ we use)
