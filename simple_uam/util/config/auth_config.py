from attrs import define, field
from .manager import Config
from .path_config import PathConfig
from typing import List, Optional

@define
class AuthConfig():
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html
    """

    isis_user : Optional[str] = field(
        default=None,
    )
    """
    Username for git.isis.vanderbilt.edu.
    """

    isis_token : Optional[str] = field(
        default=None,
    )
    """
    Auth token for git.isis.vanderbilt.edu.
    You can create one [here](https://git.isis.vanderbilt.edu/-/profile/personal_access_tokens).
    Give it read_api, and read_repository permissions.
    Will look something like "glpat-ASDsd79adAkslafo21GO".
    """

    @property
    def isis_auth(self):
        """
        Do we have git.isis.vanderbilt.edu authentication set up?
        """
        return self.isis_user and self.isis_token

# Add to the configuration manager
Config.register(
    AuthConfig,
    interpolation_key = "auth",
    conf_file = "auth.conf.yaml",
    conf_deps = [PathConfig],
)
