"""
SimpleUAM windows node setup scripts.
"""

from typing import List # noqa
from .abstract import CorpusReader
from .gremlin import GremlinCorpus
from .static import StaticCorpus

__all__: List[str] = [
    'CorpusReader',
    'GremlinCorpus',
    'StaticCorpus',
]  # noqa: WPS410 (the only __variable__ we use)
