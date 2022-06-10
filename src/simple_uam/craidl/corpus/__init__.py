"""
SimpleUAM windows node setup scripts.
"""

from typing import List # noqa
from .abstract import CorpusReader
from .gremlin import GremlinCorpus
from .static import StaticCorpus
from .get_corpus import get_corpus

__all__: List[str] = [
    'CorpusReader',
    'GremlinCorpus',
    'StaticCorpus',
    'get_corpus',
]  # noqa: WPS410 (the only __variable__ we use)
