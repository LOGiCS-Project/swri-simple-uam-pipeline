
import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, CraidlConfig
from simple_uam.util.logging import get_logger
from simple_uam.util.system import backup_file

from .gremlin import GremlinCorpus
from .static import StaticCorpus

from pathlib import Path
import json

import subprocess

log = get_logger(__name__)

def get_corpus(static = None,
               host = None,
               port = None):
    """
    Given the inputs will create a corpus object, using the configured settings
    where needed.

    Arguments:
      static: The static '.json' corpus to use when generating the files.
        Mutually exclusive with host and port. Default: As configured
      host: The hostname of the corpus server to use when generating the files.
        Mutually exclusive with static. Default: As configured
      port: The port of the corpus server to use when generating the files.
        Mutually exclusice with static. Default: As configured
    """

    mk_static = False

    if static and host:
        err = RuntimeError("Cannot have both static corpus and corpus server.")
        log.exception(
            "Cannot specify 'static' and 'host' at the same time.",
            static=static,
            host=host,
            port=port,
            err=err,
        )
        raise err
    elif not static and not host:
        if Config[CraidlConfig].use_static_corpus:
            mk_static = True
            static = True
        else:
            host = True
    elif static:
        mk_static = True

    if mk_static:

        if isinstance(static, bool) and static:
            static = Config[CraidlConfig].static_corpus
        static = Path(static)

        log.info(
            "Loading static corpus.",
            corpus_file=str(static),
        )

        with static.open() as fp:
            return StaticCorpus.load_json(fp)

    else:

        if isinstance(host, bool) and host:
            host = Config[CraidlConfig].server_host

        if not port:
            port = Config[CraidlConfig].server_port

        log.info(
            "Creating corpus client.",
            host=host,
            port=port,
        )

        return GremlinCorpus(host=host, port=port)
