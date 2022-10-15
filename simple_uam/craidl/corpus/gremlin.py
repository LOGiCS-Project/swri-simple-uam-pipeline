from attrs import define, frozen, field
from typing import List, Dict, Any, Iterator, Tuple
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

from .abstract import *
import time

from simple_uam.util.logging import get_logger

log = get_logger(__name__)

@define
class GremlinComponent(ComponentReader):
    """
    A wrapper for a component in a gremlin db, will only perform queries lazily.
    """

    parent = field()
    """
    The parent corpus.
    """

    _name = field()
    """
    The string name of this component.
    """

    @property
    def name(self) -> str:
        return self._name

    @property
    def g(self) -> str:
        return self.parent.g

    @property
    def connections(self) -> List[str]:

        return self.g.V().has('[avm]Component','[]Name',self.name) \
                   .in_('inside').hasLabel('[]Connector') \
                       .values('[]Name') \
                   .toList()

    @property
    def cad_part(self) -> Optional[str]:

        part = self.g.V().has('[avm]Component','[]Name',self.name) \
            .in_('inside').has('VertexLabel','[]DomainModel') \
                .has('[]Format','Creo') \
                .values('[]Name') \
            .toList()

        return None if len(part) == 0 else part[0]

    @property
    def cad_properties(self) -> List[Dict[str,Any]]:

        return self.g.V().has('[avm]Component','[]Name',self.name) \
            .in_('inside').hasLabel('[]DomainModel') \
                .has('[]Format','Creo') \
                .in_('inside').hasLabel('[]Parameter') \
                .as_('PROP') \
            .values('[]Name') \
                .as_('PROP_NAME') \
            .select('PROP') \
                .in_('inside').in_('inside').out('value_source') \
                .in_('inside').in_('inside').in_('inside').values('value') \
                .as_('PROP_VALUE') \
            .select('PROP_NAME','PROP_VALUE') \
            .toList()

    @property
    def cad_params(self) -> List[Dict[str,Any]]:

        return self.g.V().has('[avm]Component','[]Name',self.name) \
            .in_('inside').hasLabel('[]DomainModel') \
                .has('[]Format','Creo') \
                .in_('inside').hasLabel('[]Parameter') \
                .as_('LIB_PROP') \
            .values('[]Name') \
                .as_('PROP_NAME') \
            .select('LIB_PROP') \
                .in_('inside').in_('inside').out('value_source') \
                .in_('inside').in_('inside').hasLabel('[]AssignedValue') \
                .in_('inside').in_('inside').values('value') \
                .as_('PROP_VALUE') \
            .select('PROP_NAME','PROP_VALUE') \
            .toList()

    def cad_connection(self, conn : str) -> Optional[str]:

        conn = self.g.V().has('[avm]Component','[]Name',self.name) \
            .in_('inside').has('[]Connector','[]Name',conn) \
            .in_('inside').hasLabel('[]Role').out('port_map').values('[]Name') \
            .dedup().toList()

        return None if len(conn) == 0 else conn[0]

    @property
    def properties(self) -> List[Dict[str,Any]]:

        return self.g.V().has('[avm]Component','[]Name',self.name) \
            .in_('inside').hasLabel('[]Property') \
                .as_('C_PROP') \
            .values('[]Name') \
                .as_('PROP_NAME') \
            .select('C_PROP') \
                .in_('inside').hasLabel('[]Value') \
                .in_('inside').in_('inside').in_('inside').values('value') \
                .as_('PROP_VALUE') \
            .select('PROP_NAME','PROP_VALUE') \
            .toList()

    @property
    def params(self) -> List[Dict[str,Any]]:

        return self.g.V().has('[avm]Component','[]Name',self.name) \
            .in_('inside').hasLabel('[]Property') \
                .as_('C_PROP') \
            .values('[]Name') \
                .as_('PROP_NAME') \
            .select('C_PROP') \
                .in_('inside').hasLabel('[]Value') \
                .in_('inside').in_('inside').hasLabel('[]AssignedValue') \
                .in_('inside').in_('inside').values('value') \
                .as_('PROP_VALUE') \
            .select('PROP_NAME','PROP_VALUE') \
            .toList()

@define
class GremlinCorpus(CorpusReader):
    """
    A corpus that is backed by a gremlin compatible server.
    """

    host : Optional[str] = field(
        default=None,
    )

    port : Optional[int] = field(
        default=None,
    )

    conn_timeout : int = field(
        default=300000,
    )
    """ Connection timeout in ms. """

    eval_timeout : int = field(
        default=120000,
    )
    """ Single query timeout in ms. """

    url : str = field(
        init=False,
    )

    @url.default
    def _default_url(self):
        host = self.host or 'localhost'
        port = self.port or 8182
        return f"ws://{host}:{port}/gremlin"

    conn = field(
        init=False,
    )

    @conn.default
    def init_conn(self):
        log.info(
            'Connecting to Gremlin server...',
            server=self.url,
        )
        return traversal().withRemote(DriverRemoteConnection(self.url,'g'))

    start_time : float = field(
        init=False,
    )

    @start_time.default
    def _start_time_default(self):
        return time.monotonic()

    @property
    def g(self):
        curr_time = time.monotonic()
        elapsed = curr_time - self.start_time
        if elapsed > self.conn_timeout:
            log.info(
                "Connection timeout met, creating new connection.",
                start_time = self.start_time,
                curr_time = curr_time,
                elapsed = elapsed,
                conn_timeout = self.conn_timeout,
            )
            self.conn = self.init_conn()
            self.start_time = time.monotonic()

        return self.conn.with_('evaluationTimeout', self.eval_timeout)


    def __getitem__(self, comp : str) -> GremlinComponent:
        return GremlinComponent(self, comp)

    def __contains__(self, comp : str) -> bool:
        return self.g.V().has('[avm]Component','[]Name',comp)

    @property
    def components(self) -> Iterator[ComponentReader]:

        return self.g.V().hasLabel('[avm]Component') \
                   .values('[]Name').toList()
