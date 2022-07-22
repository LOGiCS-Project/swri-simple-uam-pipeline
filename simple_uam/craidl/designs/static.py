from attrs import define, frozen, field, setters
from typing import List, Dict, Set, Any, Iterator, Tuple, Union, Optional

import shutil
from .abstract import *

from simple_uam.util.logging import get_logger
import json
from pathlib import Path

log = get_logger(__name__)

@define
class StaticDesign(AbstractDesign):
    """
    A static component defined an an immutable object.
    """

    _rep : dict = field(
        on_setattr=setters.frozen
    )
    """ Internal object representation of a component. """

    _parameter_dict : Optional[dict] = field(
        default=None,
        init=False,
    )
    """ Internal cache of parameter dictionary. """

    _component_dict : Optional[dict] = field(
        default=None,
        init=False,
    )
    """ Internal cache of parameter dictionary. """

    _connection_set : Optional[set] = field(
        default=None,
        init=False,
    )
    """ Internal cache of connection dictionary. """

    @property
    def name(self) -> str:
        return self._rep['name']

    @property
    def extra(self) -> object:
        return self._rep['extra']

    @property
    def parameter_dict(self) -> Dict[str,DesignParameter]:
        if not self._parameter_dict:
            self._parameter_dict = {
                param.name : param for param in self.parameters
            }
        return self._parameter_dict

    @property
    def parameters(self) -> List[DesignParameter]:
        return [DesignParameter.from_rep(rep) for rep in self._rep['parameters']]

    @property
    def component_dict(self) -> Dict[str,DesignComponent]:
        if not self._component_dict:
            self._component_dict = {
                comp.instance : comp for comp in self.components
            }
        return self._component_dict

    @property
    def components(self) -> List[DesignComponent]:
        return [DesignComponent.from_rep(rep) for rep in self._rep['components']]

    @property
    def connections(self) -> Set[DesignConnection]:
        if not self._connection_set:
            self._connection_set = {
                DesignConnection.from_rep(rep) for rep in self._rep['connections']
            }
        return self._connection_set

    def add_connection(self, conn: StaticDesignConnection):
        raise RuntimeError("Cannot add connection to static design.")

    @classmethod
    def from_rep(cls, rep) -> 'StaticDesign':
        """ Load from serializable rep. """
        return cls(rep)

    @classmethod
    def load_json(cls, fp, **kwargs):
        """ Same arguments as json.load. """
        return cls.from_rep(json.load(fp,**kwargs))

    @classmethod
    def load_json_str(cls, s, **kwargs):
        """ Same arguments as json.loads. """
        return cls.from_rep(json.loads(s, **kwargs))

    def dump_json(self, fp, indent="  ", **kwargs):
        """ Same arguments as json.dump less the first. """
        return json.dump(self._rep, fp, indent=indent, **kwargs)

    def dump_json_str(indent="  ", **kwargs):
        """ Same arguments as json.dumps less the first. """
        return json.dumps(self._rep, indent=indent, **kwargs)

@frozen
class StaticDesignCorpus(AbstractDesignCorpus):
    """
    A design corpus that is backed by a static representation.
    """

    _rep : dict = field(
    )

    def __getitem__(self, design : str) -> StaticDesign:
        return StaticDesign.from_rep(self.rep[design])

    def __contains__(self, design : str) -> bool:
        return comp in rep

    @property
    def designs(self) -> List[str]:
        return self.rep.keys()

    @classmethod
    def from_rep(cls, rep) -> 'StaticDesignCorpus':
        """ Load from serializable rep. """
        return cls(rep)

    @classmethod
    def load_json(cls, fp, **kwargs):
        """ Same arguments as json.load. """
        return cls.from_rep(json.load(fp,**kwargs))

    @classmethod
    def load_json_str(cls, s, **kwargs):
        """ Same arguments as json.loads. """
        return cls.from_rep(json.loads(s, **kwargs))

    def dump_json(self, fp, indent="  ", **kwargs):
        """ Same arguments as json.dump less the first. """
        return json.dump(self.rep, fp, indent=indent, **kwargs)

    def dump_json_str(indent="  ", **kwargs):
        """ Same arguments as json.dumps less the first. """
        return json.dumps(self.rep, indent=indent, **kwargs)
