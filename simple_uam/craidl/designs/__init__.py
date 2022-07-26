"""
SimpleUAM windows node setup scripts.
"""

from typing import List # noqa
from .abstract import AbstractDesign, AbstractDesignCorpus
from .gremlin import GremlinDesign, GremlinDesignCorpus
from .static import StaticDesign, StaticDesignCorpus

__all__: List[str] = [
    'GremlinDesign',
    'GremlinDesignCorpus',
    'StaticDesign',
    'StaticDesignCorpus',
    'AbstractDesign',
    'AbstractDesignCorpus',
]  # noqa: WPS410 (the only __variable__ we use)
