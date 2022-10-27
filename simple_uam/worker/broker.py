
from simple_uam.util.config import Config, PathConfig, BrokerConfig
from simple_uam.util.logging import get_logger
from urllib.parse import urlparse
from copy import deepcopy
from pathlib import Path
from attrs import define,field
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend
from dramatiq.actor import Actor
from dramatiq.middleware import CurrentMessage

import textwrap

log = get_logger(__name__)

def default_broker():
    """
    Creates a new broker as specified by the config files
    """

    url = Config[BrokerConfig].url

    parsed = urlparse(url)

    broker = None

    ### Setup Broker ###

    if 'amqp' in parsed.scheme:
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

    broker.add_middleware(CurrentMessage())

    ### Setup Results Backend ###

    if Config[BrokerConfig].backend.enabled:

        backend = RedisBackend(
            url=Config[BrokerConfig].backend.url
        )

        broker.add_middleware(Results(
            backend=backend,
            store_results=True
        ))

    return broker

# Initialize the system broker based on the default.
_BROKER = default_broker()
dramatiq.set_broker(_BROKER)

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
        broker=_BROKER,
        **options,
    )

def message_metadata():
    """
    When called in a running actor provides a dictionary of metadata from the
    message being processed.

    Returns:
      None if not in actor context, otherwise a dict with assorted
      metadata from the current message.
    """

    msg = CurrentMessage.get_current_message()

    if msg:
        # I copy things into a new dict to better control what
        # properties are preserved.
        return deepcopy(dict(
            queue_name = msg.queue_name,
            actor_name = msg.actor_name,
            message_id = msg.message_id,
            message_timestamp = msg.message_timestamp,
            args=msg.args,
            kwargs=msg.kwargs,
        ))
    else:
        return None

def has_backend():
    """
    Returns whether there is a backend for returning message results.
    """

    return Config[BrokerConfig].backend.enabled
