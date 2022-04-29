from attrs import define, field
from typing import TypeVar, Type, List, Dict, Optional, Union, Any
from omegaconf import  OmegaConf
from pathlib import Path
import argparse
from .path_config import PathConfig, PATHCONFIG_INTERPOLATION_KEY, PATHCONFIG_FILE_NAME

@define
class ConfigType():
    """
    Metadata for a single config file used by this project.
    """

    parent_mgr : 'ConfigManager' = field()
    """ The parent manager this config info object belongs to """

    data_cls : Type = field()
    """ Structured Config Class for this Config """

    interpolation_key : str = field()
    """ The key for associated interpolation resolver """

    conf_file : Path = field(converter=Path)
    """ The config file for this obj, taken relative to the config_dir root """

    conf_deps : List[Type] = field(factory=dict)
    """ Config Classes that this depends on (for interpolation) """

    conf_obj : Optional[OmegaConf] = field(default=None, init=False)
    """ Runtime OmegaConf Object for this Data """

    @property
    def config(self) -> OmegaConf:
        """
        Retrieves the config for external use,
        """
        if self.conf_obj: return self.conf_obj

        # Using the parent get list of ordered config files
        # Create object w/ dataclass and loaded individual files
        # Register resolvers for each configuration dependency
        # Save the config and set as read-only
        # set self.conf_obj to new variable

        # return self.conf_obj

        raise NotImplementedError()

T = TypeVar('T', bound='ConfigManager')

@define
class ConfigManager(object):
    """
    Singleton, project-wide manager of configuration files.
    """

    config_types : Dict[Type, ConfigType] = field(factory=dict)
    """ Dict of all the configuration types we manage """

    config_dirs : List[Path] = field(factory=list)
    """ The search path of configuration directories """

    def __new__(cls):
        """
        Creates a singleton object, if it is not created,
        or else returns the previous singleton object
        """

        if not hasattr(cls, 'instance'):
            cls.instance = super(ConfigManager, cls).__new__(cls)
        return cls.instance

    def __attrs__post_init__(self):

        # Read args (non-destructively)
        # Load PathConfig
        # Populate config_dirs
        # Add PathConfig to config_types

        raise NotImplementedError()

    def config_search_path(self, config_file : Union[str,Path]) -> List[Path]:
        """
        Gives the search path to use for a particular file, with later paths
        over-riding earlier ones.
        """

        raise NotImplementedError()



    def register(
            self,
            data_cls : Type,
            interpolation_key : str,
            conf_file : Union[str, Path],
            conf_deps : List[Type] = []
    ) -> None:
        """
        Registers a configuration dataclass with the manager.
        Raises an error if the operation fails.

        Arguments:
            data_cls: The dataclass or attrs class that represents the
                contents of the file.
            interpolation_key: The string used to specify the resolver for this
                config in other configs. E.g. If the data_cls has a field
                "name" and the resolve_key is "example_conf" then other
                configurations can use "${example_conf:name}" in their string
                interpolations.
            conf_file: The config file associated with this object, specified
                relative to the config_dir.
            conf_deps: The config classes used for interpolations in this one.
        """

        # If already registered error
        # Create object

        raise NotImplementedError()

    def get(self, data_cls : Type[T]) -> T:
        """
        Retrieves an OmegaConf object for the associated dataclass type.

        Arguments:
            data_cls: The dataclass or attrs class that represents the
                contents of the file.

                Note: this must have been previously registered.
        """

        raise NotImplementedError()

    def get_argparser(self) -> argparse.ArgumentParser:
        """
        Get the arg parser for the conf_dir and run_mode options.
        """

        raise NotImplementedError()
