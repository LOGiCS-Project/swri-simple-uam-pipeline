
from simple_uam.util.config import Config, PathConfig, D2CWorkerConfig
from simple_uam.util.logging import get_logger
from urllib.parse import urlparse
from pathlib import Path
from attrs import define,field
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend
from dramatiq.actor import Actor

import textwrap

log = get_logger(__name__)

def default_broker():
    """
    Creates a new broker as specified by the config files
    """

    url = Config[D2CWorkerConfig].broker.url

    parsed = urlparse(url)

    broker = None

    ### Setup Broker ###

    if parsed.scheme == 'amqp':
        broker = RabbitmqBroker(url=url)
    elif parsed.scheme == 'redis':
        broker = RedisBroker(url=url)
    else:
        err = RuntimeError("Unsupported broker protocol.")
        log.exception(
            "Broker schema must be 'amqp' (for rabbitmp) or 'redis' (for redis).",
            url=url,
            schema=parsed.scheme,
        )
        raise err

    ### Setup Results Backend ###

    if Config[D2CWorkerConfig].backend.enabled:

        backend = RedisBackend(
            url=Config[D2CWorkerConfig].backend.url
        )

        broker.add_middleware(Results(backend=backend))

    return broker

# Initialize the system broker based on the default.
__BROKER = default_broker()
dramatiq.set_broker(__BROKER)

def actor(fn=None,
          *,
          actor_class=Actor,
          actor_name=None,
          queue_name='default',
          priority=0,
          **options):
    """
    Wraps 'dramatiq.actor', so the options and defaults are mostly the same.

    Changes:
      - Default actor names are distinguished by modules. This applies even
        when a specific name is given. If you want to have complete control
        use 'dramatiq.actor' directly.
      - There is no 'broker' option, it's fixed to the one initialized in
        this modules.

    See: https://dramatiq.io/reference.html#dramatiq.actor
    """
    actor_name = actor_name or fn.__name__
    actor_name = f"{fn.__module__}:{actor_name}"

    return dramatiq.actor(
        fn=fn,
        actor_class=actor_class,
        actor_name=actor_name,
        queue_name=queue_name,
        priority=priority,
        broker=__BROKER,
        **options,
    )