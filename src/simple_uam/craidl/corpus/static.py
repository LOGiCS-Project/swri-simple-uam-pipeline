from attrs import define, frozen, field
from typing import List, Dict, Any, Iterator, Tuple

from .abstract import *

from simple_uam.util.logging import get_logger

log = get_logger(__name__)

@frozen
class StaticComponent(ComponentReader):
    """
    A static component defined an an immutable object.
    """

    rep : dict = field(
        frozen=True,
    )
    """ Internal object representation of a component. """

    @property
    def name(self) -> str:
        return self.rep['name']

    @property
    def connections(self) -> List[str]:
        return list(self.rep.get('conns',dict()).keys())

    @property
    def cad_part(self) -> Optional[str]:
        return self.rep.get('cad_part')

    @property
    def cad_properties(self) -> List[Dict[str,Any]]:
        return self.rep.get('cad_props',list())

    @property
    def cad_params(self) -> List[Dict[str,Any]]:
        return self.rep.get('cad_params',list())

    @property
    def cad_connection(self, conn : str) -> Optional[str]:
        return self.rep.get('conns',dict()).get(conn,dict()).get('cad')

    @property
    def properties(self) -> List[Dict[str,Any]]:
        return self.rep.get('props',list())

    @property
    def params(self) -> List[Dict[str,Any]]:
        return self.rep.get('params',list())

    @classmethod
    def from_rep(cls, rep) -> StaticComponent:
        """ Load from serializable rep. """
        return cls(rep)

    def to_rep(self):
        """ Return the rep. """
        return self.rep

    @staticmethod
    def component_rep(comp : ComponentReader) -> dict:
        """ Extract the rep from a component. """

        rep = dict()

        rep['name'] = comp.name

        conns = dict()
        for conn in comp.connections:
            conns[conn] = dict()
            if cad_conn := comp.cad_connection(conn):
                conns[conn]['cad'] = cad_conn
        rep['conns'] = conns

        if cad_part := comp.cad_part:
            rep['cad_part'] = cad_part

        cad_props = comp.cad_properties
        if len(cad_props) > 0:
            rep['cad_props'] = cad_props

        cad_params = comp.cad_params
        if len(cad_props) > 0:
            rep['cad_params'] = cad_params

        props = comp.properties
        if len(props) > 0:
            rep['props'] = props

        params = comp.params
        if len(params) > 0:
            rep['params'] = params

        return rep

    @classmethod
    def from_component(cls, comp : ComponentReader) -> StaticComponent:
        return cls.from_rep(cls.component_rep(comp))


@frozen
class StaticCorpus(CorpusReader):
    """
    A corpus that is backed by a static representation.
    """

    rep : dict = field(
        frozen=True,
    )

    def __getitem__(self, comp : str) -> ComponentReader:
        return StaticComponent.from_rep(self.rep[comp])

    @property
    def components(self) -> Iterator[ComponentReader]:
        return self.rep.keys()

    @classmethod
    def from_rep(cls, rep) -> StaticCorpus:
        """ Load from serializable rep. """
        return cls(rep)

    def to_rep(self):
        """ Return the rep. """
        return self.rep

    @staticmethod
    def corpus_rep(cls, corp : CorpusReader) -> dict:
        rep = dict()

        for comp in corp.components:
            rep[comp] = ComponentReader.component_rep(corp[comp])

        return rep

    @classmethod
    def from_corpus(cls, corp : CorpusReader) -> StaticCorpus:
        """ Extract the rep from a component. """

        return cls.from_rep(cls.corpus_rep(corp))
