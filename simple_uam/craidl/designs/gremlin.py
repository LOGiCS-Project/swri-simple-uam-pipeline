from attrs import define, frozen, field
from typing import List, Dict, Any, Iterator, Tuple, Set, Optional
from urllib.parse import urlparse

# All the recommended imports, see
# http://tinkerpop.apache.org/docs/current/reference/#python-imports
from gremlin_python import statics
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import T, Order, Cardinality, Column, \
    Direction, Operator, P, Pop, Scope, Barrier, Bindings, WithOptions

from .abstract  import *
from .static    import *
from ..gremlin import GremlinConnection
import time
import json

from simple_uam.util.logging import get_logger

log = get_logger(__name__)

@define
class GremlinDesign(AbstractDesign):
    """
    A specific parameter in this gremlin design.
    """

    parent = field()
    """
    The parent corpus.
    """

    _name : str = field()
    """
    The string name of this design
    """

    _extra : object = field(
        factory = dict
    )
    """
    extra design info
    """

    @property
    def name(self) -> str:
        return self._name

    @property
    def extra(self) -> str:
        return self._extra

    @property
    def g(self) -> str:
        return self.parent.g

    _parameter_dict : Optional[Dict[str,DesignParameter]] = field(
        default = None,
    )

    def get_design_params(self):
        return self.g.V().has('[avm]Design','[]Name',self.name) \
            .in_('inside').hasLabel('[]RootContainer') \
            .in_('inside').hasLabel('[]Property').as_('name') \
            .in_('inside').hasLabel('[]Value').as_('val') \
            .in_('inside').hasLabel('[]ValueExpression') \
            .in_('inside').hasLabel('[]AssignedValue') \
            .in_('inside').hasLabel('[]Value') \
            .in_('inside').as_('value') \
            .select('val') \
            .in_('value_source').out('inside').out('inside').hasLabel('[]PrimitivePropertyInstance').as_('ci_prop') \
            .out('inside').hasLabel('[]ComponentInstance').as_('ci') \
            .select('name','value','ci_prop','ci') \
            .by('[]Name').by('value').by('[]CName').by('[]Name') \
            .toList()

    @property
    def parameter_dict(self) -> Dict[str,DesignParameter]:
        if self._parameter_dict == None:

            # Init dict
            self._parameter_dict = dict()

            # Group by param name
            for param in self.get_design_params():

                log.info(
                    "Loading design param from db",
                    name=self.name,
                    param=param,
                    #param=json.dumps(param, indent="  "),
                )

                name = param['name']
                value = param['value']

                if name not in self._parameter_dict:
                    self._parameter_dict[name] = DesignParameter(
                        name=name,
                        value=value,
                    )

                self._parameter_dict[name].add_property(
                    DesignProperty(
                        instance_name = param['ci'],
                        property_name = param['ci_prop'],
                    )
                )

        return self._parameter_dict


    _component_dict : Optional[Dict[str,DesignComponent]] = field(
        default = None,
    )

    def get_untyped_component_instances(self):
        return self.g.V().has('[avm]Design','[]Name',self.name) \
            .in_('inside').hasLabel('[]RootContainer') \
            .in_('inside').hasLabel('[]ComponentInstance').as_('component_instance') \
            .out('component_id').out('component_instance').as_('component_choice') \
            .in_('inside').hasLabel('[]Classifications') \
            .not_(__.in_('inside')) \
            .select('component_instance', 'component_choice') \
            .by('[]Name').by('[]Name') \
            .dedup() \
            .toList()

    def get_component_instances(self):
        return self.g.V().has('[avm]Design','[]Name',self.name) \
            .in_('inside').hasLabel('[]RootContainer') \
            .in_('inside').hasLabel('[]ComponentInstance').as_('component_instance') \
            .out('component_id').out('component_instance').as_('component_choice') \
            .in_('inside').hasLabel('[]Classifications') \
            .in_('inside').as_('component_type') \
            .select('component_instance', 'component_type', 'component_choice') \
            .by('[]Name').by('value').by('[]Name') \
            .dedup() \
            .toList()

    @property
    def component_dict(self) -> Dict[str,DesignComponent]:
        if self._component_dict == None:

            self._component_dict = dict()

            for inst_rep in self.get_component_instances():
                comp = DesignComponent.from_rep(inst_rep)
                log.info(
                    "Adding DB component to design.",
                    name=self.name,
                    comp=comp,
                )
                self._component_dict[comp.instance] = comp

            for inst_rep in self.get_untyped_component_instances():
                comp = DesignComponent.from_rep(inst_rep)
                log.info(
                    "Adding untyped DB component to design.",
                    name=self.name,
                    comp=comp,
                )
                self._component_dict[comp.instance] = comp

        return self._component_dict

    _connection_set : Optional[Set[DesignConnection]] = field(
        default = None,
    )

    def get_connections(self):
        return self.g.V().has('[avm]Design','[]Name',self.name) \
            .in_('inside').hasLabel('[]RootContainer') \
            .in_('inside').hasLabel('[]ComponentInstance').as_('from_ci') \
            .in_('inside').hasLabel('[]ConnectorInstance').as_('from_conn') \
            .in_('connector_composition').hasLabel('[]ConnectorInstance').as_('to_conn') \
            .out('inside').hasLabel('[]ComponentInstance').as_('to_ci') \
            .select('from_ci','from_conn','to_ci','to_conn') \
            .by('[]Name').by('[]Name').by('[]Name').by('[]Name') \
            .dedup() \
            .toList()

    @property
    def connections(self) -> Set[DesignConnection]:
        if self._connection_set == None:

            self._connection_set = set()

            for conn_rep in self.get_connections():

                conn = DesignConnection.from_rep(conn_rep)
                if conn in self._connection_set:
                    log.warning(
                        "Already found connection in design",
                        name=self.name,
                        conn=conn,
                        # conn=json.dumps(conn.rep, indent="  "),
                    )
                else:
                    log.info(
                        "Adding DB connection to design.",
                        name=self.name,
                        conn=conn,
                        # conn=json.dumps(conn.rep, indent="  "),
                    )

                    self._connection_set.add(conn)
        return self._connection_set

    def add_connection(self, conn: DesignConnection):
        self._connection_set.add(conn)

@define
class GremlinDesignCorpus(AbstractDesignCorpus):
    """
    A corpus that is backed by a gremlin compatible server.
    """

    conn : GremlinConnection = field()

    @property
    def g(self):
        return self.conn.g

    def __getitem__(self, design : str) -> GremlinDesign:
        return GremlinDesign(self, design)

    def __contains__(self, design : str) -> bool:
        return self.g.V().has('[avm]Design','[]Name',design)

    @property
    def designs(self) -> Iterator[str]:
        return self.g.V().hasLabel('[avm]Design') \
                   .values('[]Name').toList()
