from attrs import define, field
from util.config import Config, PathConfig
from typing import Optional, List, Any

@define
class CeleryConfig():
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html

    This contains options as defined in: https://docs.celeryq.dev/en/stable/userguide/configuration.html
    If the names match we can just use the CeleryConfig object directly as
    when initializing a Celery Object.
    """

    result_backend : Optional[str] = None
    """
    Backend for result, see: https://docs.celeryq.dev/en/stable/userguide/configuration.html#result-backend

    Set to something in following format if needed:
      - "mode+scheme://user:password@host:port"
      - "redis://username:password@host:port/db"

    """

    broker_url : str = "amqp://"
    """
    Default message broker URL.

    Must be in form: "transport://userid:password@hostname:port/virtual_host"

    See: https://docs.celeryq.dev/en/stable/userguide/configuration.html#broker-url
    """

# Add to the configuration manager
Config.register(
    CeleryConfig,
    interpolation_key = "celery",
    conf_file = "celery.conf.yaml",
    conf_deps = [PathConfig],
)
