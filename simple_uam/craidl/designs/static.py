from attrs import define, frozen, field, setters
from typing import List, Dict, Any, Iterator, Tuple, Union, Optional

import shutil
from .abstract import *

from simple_uam.util.logging import get_logger
import json
from pathlib import Path

log = get_logger(__name__)

@define
class StaticDesignParameter(AbstractDesignParameter):
    """
    A static component defined an an immutable object.
    """

    rep : dict = field(
    )
    """ Internal object representation of a component. """

    @property
    def name(self) -> str:
        return self.rep['name']

    @property
    def value(self) -> str:
        return self.rep['value']

    @property
    def properties(self) -> List[DesignParameterProperty]:
        return [
            DesignParameterProperty(
                instance_name = prop['component_name'],
                property_name  = prop['component_property']
            )
            for prop in self.rep['component_properties']
        ]

    @property
    def component_properties(self) -> List[Dict[str,str]]:
        return self.rep['component_properties']

    def add_property(self, prop: DesignParameterProperty):
        self.rep['component_properties'].append(prop.rendered())

    @classmethod
    def from_rep(cls, rep) -> 'StaticDesignParameter':
        """ Load from serializable rep. """
        return cls(rep)

    def to_rep(self):
        """ Return the rep. """
        return self.rep

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

@frozen
class StaticDesignComponent(AbstractDesignComponent):
    """
    A static component defined an an immutable object.
    """

    rep : dict = field(
    )
    """ Internal object representation of a component. """

    @property
    def instance(self) -> str:
        return self.rep['component_instance']

    @property
    def type(self) -> Optional[str]:

        # log.info(json.dumps(self.rep, indent="  "))
        if 'component_type' in self.rep:
            return self.rep['component_type']
        else:
            return None

    @property
    def choice(self) -> str:
        return self.rep['component_choice']

    @classmethod
    def from_rep(cls, rep) -> 'StaticDesignComponent':
        """ Load from serializable rep. """
        return cls(rep)

    def to_rep(self):
        """ Return the rep. """
        return self.rep

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

@frozen
class StaticDesignConnection(AbstractDesignConnection):
    """
    A static connection defined an an immutable object.
    """

    rep : dict = field(
    )
    """ Internal object representation of a component. """

    @property
    def from_side(self) -> DesignConnector:
        return DesignConnector(
            instance = self.rep['from_ci'],
            conn_type = self.rep['from_conn'],
        )

    @property
    def to_side(self) -> DesignConnector:
        return DesignConnector(
            instance = self.rep['to_ci'],
            conn_type = self.rep['to_conn'],
        )

    @classmethod
    def from_rep(cls, rep) -> 'StaticDesignConnection':
        """ Load from serializable rep. """
        return cls(rep)

    def to_rep(self):
        """ Return the rep. """
        return self.rep

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

@define
class StaticDesign(AbstractDesign):
    """
    A static component defined an an immutable object.
    """

    rep : dict = field(
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

    _connection_dict : Optional[dict] = field(
        default=None,
        init=False,
    )
    """ Internal cache of connection dictionary. """

    @property
    def name(self) -> str:
        return self.rep['name']

    @property
    def extra(self) -> object:
        return self.rep['extra']

    @property
    def parameter_dict(self) -> Dict[str,StaticDesignParameter]:
        if not self._parameter_dict:
            self._parameter_dict = {
                param.name : param for param in self.parameters
            }
        return self._parameter_dict

    @property
    def parameters(self) -> List[StaticDesignParameter]:
        return [StaticDesignParameter(rep) for rep in self.rep['parameters']]

    @property
    def component_dict(self) -> Dict[str,StaticDesignComponent]:
        if not self._component_dict:
            self._component_dict = {
                comp.instance : comp for comp in self.components
            }
        return self._component_dict

    @property
    def components(self) -> List[StaticDesignComponent]:
        return [StaticDesignComponent(rep) for rep in self.rep['components']]

    @property
    def connection_dict(self) -> Dict[DesignConnector, StaticDesignConnection]:
        if not self._connection_dict:
            self._connection_dict = dict()
            for conn in self.connections:
                self._connection_dict[conn.from_side] = conn
                self._connection_dict[conn.to_side] = conn
        return self._connection_dict

    @property
    def connections(self) -> List[StaticDesignConnection]:
        return [StaticDesignConnection(rep) for rep in self.rep['connections']]

    def add_connection(self, conn: StaticDesignConnection):
        raise RuntimeError("Cannot add connection to static design.")

    @classmethod
    def from_rep(cls, rep) -> 'StaticDesign':
        """ Load from serializable rep. """
        return cls(rep)

    def to_rep(self):
        """ Return the rep. """
        return self.rep

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

@frozen
class StaticDesignCorpus(AbstractDesignCorpus):
    """
    A design corpus that is backed by a static representation.
    """

    rep : dict = field(
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

    def to_rep(self):
        """ Return the rep. """
        return self.rep

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
