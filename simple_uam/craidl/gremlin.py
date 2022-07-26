from attrs import define, frozen, field
from typing import List, Dict, Any, Iterator, Tuple, Optional, Set

import time
import json

from simple_uam.util.logging import get_logger

log = get_logger(__name__)
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


@define
class GremlinConnection():

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

    _is_open : bool = field(
        default=False,
        init=False,
    )
    """
    Is the connection currently open?
    """

    @property
    def is_open(self) -> bool:
        """
        Is the connection currently open?
        """
        return self._is_open

    _remote = field(
        default=None,
        init=False,
    )

    def _init_remote(self):
        log.info(
            'Creating Remote to Gremlin server...',
            server=self.url,
        )
        self._remote = DriverRemoteConnection(self.url,'g')


    _conn = field(
        default=None,
        init=False,
    )

    _conn_time : Optional[float] = field(
        default=None,
        init=False,
    )

    def _init_conn(self):
        log.info(
            'Starting Connection...',
            server=self.url,
        )
        self._conn = traversal().withRemote(self._remote)
        self._conn_time = time.monotonic()

    def open(self):
        """
        Open the connection.
        """

        if self.is_open:
            raise RuntimeError(
                f"Cannot reopen open connection to '{self.url}'"
            )

        self._is_open = True
        self._init_remote()
        self._init_conn()

    def close(self):
        """
        Close the connection.
        """

        if not self.is_open:
            raise RuntimeError(
                f"Cannot close already closed connection to '{self.url}'"
            )

        self._is_open = False

        self._remote.close()
        self._remote = None
        self._conn = None
        self._conn_time = None

    def reset(self):
        """
        Reset the connection.
        """
        log.info(
            "Resetting connection.",
            url=self.url,
            conn_time = self._conn_time,
            curr_time = time.monotonic(),
            conn_timeout = self.conn_timeout,
        )
        self.close()
        self.open()

    @property
    def open_time(self):
        return time.monotonic() - self._conn_time

    @property
    def g(self):
        if self.open_time > (self.conn_timeout / 1000):
            self.reset()
        return self._conn.with_('evaluationTimeout', self.eval_timeout)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, e_type, e_val, e_tb):
        self.close()
