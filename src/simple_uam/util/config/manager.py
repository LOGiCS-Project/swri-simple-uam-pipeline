import argparse
import functools
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from attrs import define, field
from attrs.setters import frozen
from invoke import Argument
from omegaconf import OmegaConf

from ..system.backup import backup_file

from .path_config import PATHCONFIG_FILE_NAME, \
    PATHCONFIG_INTERPOLATION_KEY, PathConfig

# No logging in Config because we might use config files to initialize logging

@define
class ConfigData:
    """
    Metadata for a single config file used by this project.
    """

    data_cls: Type = field(
        on_setattr=frozen,
    )
    """ Structured Config Class for this Config """

    interpolation_key: str = field(
        on_setattr=frozen,
    )
    """ The key for associated interpolation resolver """

    conf_file: Path = field(
        converter=Path,
        on_setattr=frozen,
    )
    """ The config file for this obj, taken relative to the config_dir root """

    conf_deps: List[Type] = field(
        factory=dict,
        on_setattr=frozen,
    )
    """ Config Classes that this depends on (for interpolation) """

    default_conf: Optional[OmegaConf] = field(
        default=None,
        on_setattr=frozen,
    )
    """ The default config that serves as the root of the config tree """

    load_path: List[Path] = field(
        factory=list,
        on_setattr=frozen,
    )
    """ The list of files to load on conf init """

    overrides: Optional[OmegaConf] = field(
        default=None,
        on_setattr=frozen,
    )
    """
    A dictionary of values that will override all others when this config
    is instantiated. I.e. config files can't change it. This is usually where
    the command line flags, or unchangable settings go.
    """

    conf_obj: Optional[OmegaConf] = field(
        default=None,
        init=False,
    )
    """ Runtime OmegaConf Object for this Data """

    @property
    def config(self) -> OmegaConf:
        """
        Retrieves the config for external use,
        """
        if self.conf_obj:
            return self.conf_obj

        # Assemble list of configs to merge
        configs = list()
        configs.append(OmegaConf.structured(self.data_cls))
        if self.default_conf:
            configs.append(self.default_conf)
        configs = [*configs, *self._load_configs()]
        if self.overrides:
            configs.append(self.overrides)

        # Generate merged conf
        conf = OmegaConf.merge(*configs)

        # Set as read-only
        OmegaConf.set_readonly(conf, True)

        # Save conf to instance and return
        self.conf_obj = conf
        return self.conf_obj

    @property
    def resolver(self) -> Callable[[str], str]:
        """
        Registers the resolver for this class if possible.

        Should only be called once per class.
        """

        def resolve_func(conf_dat : ConfigData, key: Optional[str] = None):
            if key:
                val = OmegaConf.select(conf_dat.config, key, default=None)
                if val is None:
                    val = getattr(conf_dat.obj, key, None)
                return val
            else:
                return conf_dat.config

        return functools.partial(resolve_func, conf_dat=self)

    def _load_configs(self) -> List[OmegaConf]:
        """
        Will load all existing configs in load_path
        """

        configs = list()

        for conf_path in self.load_path:
            if conf_path.exists():
                if not conf_path.is_file():
                    raise RuntimeError(f"Object at '{conf_path}' is not a file.")
                else:
                    configs.append(OmegaConf.load(conf_path))

        return configs

    @property
    def yaml(self) -> str:
        """Returns a YAML rep of the current config object."""
        return OmegaConf.to_yaml(self.config)

    @property
    def obj(self) -> Any:
        """
        Returns a true instance of the config object, rather than a duck
        typed wrapper with lazy loading.
        """
        return OmegaConf.to_object(self.config)

    def write_config(
        self,
        path: Union[None, List[Path], List[str], Path, str] = None,
        mkdir: bool = True,
        write_all: bool = False,
        overwrite: bool = False,
        comment: bool = True,
        fields: Optional[List[str]] = None,
        data: Optional[Any] = None,
    ):
        """
        Writes a sample config out to the filesystem.

        Arguments:
          path (default = None): Paths to write config stubs to.
            If none and write_all then all files on load path are written.
            If None and not write_all only the final file on load_path is written.
          mkdir (default =True): Create directories for config files if needed.
            If false will fail with warning when directory is missing.
          write_all (default=False): Do we create all config files on path or
            just the terminal one? (ignored if path is provided)
          overwrite: Do we overwrite files if they already exist?
          comment: Should our sample be written as a comment or as a literal
            yaml document?
          fields (default=None): what fields should be written out to the config
            file (as a subset of the available fields, in omegaconf selector format).
            Ignored if data is provided.
          data (default=None): Data to write to config, if not the currently
            loaded configuration. In some format that can be written to yaml.
        """

        # Normalize path argument.
        if path == None and write_all:
            path = self.load_path
        elif path == None and not write_all:
            path = list(self.load_path[-1:])

        if isinstance(path, list):
            path = [Path(f) for f in path]
        else:
            path = [Path(f)]

        # Organize data to write
        conf = OmegaConf.create()
        if data == None and fields:
            for field in fields:
                OmegaConf.update(
                    conf,
                    field,
                    OmegaConf.select(self.config, field),
                )
        elif data == None and not fields:
            conf = self.config
        else:
            conf = OmegaConf.create(data)

        # Get Printed Str
        yaml = OmegaConf.to_yaml(conf)
        if comment:
            yaml = "".join([f"# {line}" for line in yaml.splitlines(True)])

        # Write to each file in the path.
        for f in path:

            # Create dir if needed
            if mkdir:
                f.parent.mkdir(parents=True, exist_ok=True)

            # Create backup if overwriting
            if overwrite and f.exists():
                backup_file(f, delete=True)

            # Write if no file exists
            if not f.exists():
                f.write_text(yaml)


T = TypeVar("T")


@define
class Config(object):
    """
    Singleton, project-wide manager of configuration files.
    """

    config_types: Dict[Type, ConfigData] = field(
        factory=dict,
        init=False,
    )
    """ Dict of all the configuration types we manage """

    key_map: Dict[str, Type] = field(
        factory=dict,
        init=False,
    )
    """ Dict of interpolation keys we manage."""

    name_map: Dict[str, Type] = field(
        factory=dict,
        init=False,
    )
    """ Dict from type name to key map."""

    file_map: Dict[str, Type] = field(
        factory=dict,
        init=False,
    )
    """ Dict from file name to key map."""

    config_dirs: List[Path] = field(
        factory=list,
        init=False,
    )
    """ The search path of configuration directories """

    mode_flags: List[str] = field(factory=list, init=False)
    """ The lode flags from lowest to highest priority """

    def __new__(cls):
        """
        Creates a singleton object, if it is not created,
        or else returns the previous singleton object
        """

        if not hasattr(cls, "instance"):
            instance = super(Config, cls).__new__(cls)
            instance.__init__()
            instance.__attrs_init__()
            instance.__post_init__()
            cls.instance = instance

        return cls.instance

    def __init__(self):
        pass

    def __post_init__(self) -> None:

        # Read args (non-destructively)
        parser = self._get_argparser()
        (args, remainder) = parser.parse_known_args()

        # Update sys args w/ unused options
        # sys.argv = remainder

        # Set path from args
        self.mode_flags = args.run_mode
        self.config_dirs = [*self._get_conf_dir_chain(), *args.config_dir]

        # Load PathConfig
        path_conf_data = ConfigData(  # type: ignore[call-arg]
            data_cls=PathConfig,
            interpolation_key=PATHCONFIG_INTERPOLATION_KEY,
            conf_file=PATHCONFIG_FILE_NAME,
            conf_deps=[],
            default_conf=OmegaConf.structured(PathConfig()),
            load_path=self._search_path(PATHCONFIG_FILE_NAME),
            overrides=None,
        )

        # Add PathConfig to config_types
        self._add_conf_data(path_conf_data)

    def _add_conf_data(self, conf_data: ConfigData) -> None:

        data_cls = conf_data.data_cls

        # Register resolvers for deps
        OmegaConf.register_new_resolver(
            conf_data.interpolation_key,
            conf_data.resolver,
        )
        # print(f"registering: {data_cls}")
        self.config_types[data_cls] = conf_data
        self.key_map[conf_data.interpolation_key] = data_cls
        self.file_map[conf_data.conf_file] = str(data_cls)
        self.name_map[data_cls.__name__] = data_cls
        # print(f"registering: {self.name_map.keys()}")

    def _get_conf_dir_chain(self) -> List[Path]:
        """
        Returns the chain of config_dirs to load.
        """

        current_dir = Path(PathConfig().config_dir)
        conf_dirs = [current_dir]
        path_conf = current_dir / PATHCONFIG_FILE_NAME

        while current_dir and path_conf.is_file():
            conf = OmegaConf.load(path_conf)
            current_dir = OmegaConf.select(conf, "config_directory")
            if current_dir:
                current_dir = Path(current_dir)
                conf_dirs.append(current_dir)
                path_conf = current_dir / PATHCONFIG_FILE_NAME

        return conf_dirs

    def _search_path(self, config_file: Union[str, Path]) -> List[Path]:
        """
        Gives the search path to use for a particular file, with later paths
        over-riding earlier ones.
        """

        path_list = list()

        for mode_flag in [None, *self.mode_flags]:
            for conf_dir in self.config_dirs:
                if not mode_flag:
                    path_list.append(conf_dir / config_file)
                else:
                    path_list.append(conf_dir / mode_flag / config_file)

        return path_list

    @classmethod
    def configs(cls) -> List[Type]:
        """
        Returns a list of config dataclass types
        """
        return list(cls().config_types.keys())

    @classmethod
    def config_names(cls) -> List[str]:
        """
        Returns a list of config dataclass type names
        """
        return list(cls().name_map.keys())

    @classmethod
    def config_files(cls) -> List[str]:
        """
        Returns a list of config dataclass file locs. (relative to config dir
        root)
        """
        return list(cls().file_map.keys())

    @classmethod
    def config_keys(cls) -> List[str]:
        """
        Returns a list of config dataclass interpolation keys
        """
        return list(cls().key_map.keys())

    @classmethod
    def load_path(cls, data_cls: Union[str, Type]) -> List[Path]:
        """
        returns the list of files that are loaded for a given config dataclass.
        """
        return cls()._load_path(data_cls)

    def _load_path(self, data_cls: Union[str, Type]) -> List[Path]:
        """
        returns the list of files that are loaded for a given config dataclass.
        """
        return self.config_types[self._get_config_class(data_cls)].load_path

    @classmethod
    def write_configs(
        cls,
        configs: Optional[List[Union[str, Type]]] = None,
        mkdir: bool = True,
        write_all: bool = False,
        overwrite: bool = False,
        comment: bool = True,
        fields: Optional[List[str]] = None,
        data: Optional[Any] = None,
    ):
        """
        Writes a sample config out to the filesystem.

        Arguments:
          configs: The list of config files to write (default: All)
          mkdir (default =True): Create directories for config files if needed.
            If false will fail with warning when directory is missing.
          write_all (default=False): Do we create all config files on path or
            just the terminal one? (ignored if path is provided)
          overwrite: Do we overwrite files if they already exist?
          comment: Should our sample be written as a comment or as a literal
            yaml document?
          fields (default=None): what fields should be written out to the config
            file (as a subset of the available fields, in omegaconf selector format).
            Ignored if data is provided.
          data (default=None): Data to write to config, if not the currently
            loaded configuration. In some format that can be written to yaml.
        """
        return cls()._write_configs(
            configs=configs,
            mkdir=mkdir,
            write_all=write_all,
            overwrite=overwrite,
            comment=comment,
            fields=fields,
            data=data,
        )

    def _write_configs(
        self,
        configs: Optional[List[Union[str, Type]]] = None,
        mkdir: bool = True,
        write_all: bool = False,
        overwrite: bool = False,
        comment: bool = True,
        fields: Optional[List[str]] = None,
        data: Optional[Any] = None,
    ):
        """
        Writes a sample config out to the filesystem.

        Arguments:
          configs: The list of config files to write (default: All)
          mkdir (default =True): Create directories for config files if needed.
            If false will fail with warning when directory is missing.
          write_all (default=False): Do we create all config files on path or
            just the terminal one? (ignored if path is provided)
          overwrite: Do we overwrite files if they already exist?
          comment: Should our sample be written as a comment or as a literal
            yaml document?
          fields (default=None): what fields should be written out to the config
            file (as a subset of the available fields, in omegaconf selector format).
            Ignored if data is provided.
          data (default=None): Data to write to config, if not the currently
            loaded configuration. In some format that can be written to yaml.
        """
        conf_types = None
        if configs == None:
            conf_types = self.config_types.values()
        else:
            conf_types = [self.config_types[self._get_config_class(config)] for config in configs]

        for conf_type in conf_types:
            conf_type.write_config(
                write_all=write_all,
                overwrite=overwrite,
                comment=comment,
                fields=fields,
                data=data,
            )

    @classmethod
    def register(
        cls, data_cls: Type, interpolation_key: str, conf_file: Union[str, Path], conf_deps: List[Type] = []
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

        cls()._register(
            data_cls=data_cls,
            interpolation_key=interpolation_key,
            conf_file=conf_file,
            conf_deps=conf_deps,
        )

    def _register(
        self, data_cls: Type, interpolation_key: str, conf_file: Union[str, Path], conf_deps: List[Type] = []
    ) -> None:
        """
        See register for details
        """

        # If already registered error
        if data_cls in self.config_types:
            raise RuntimeError(f"Class {data_cls.__name__} already registered with Config.")

        # Check dependent configs are installed
        for par_cls in conf_deps:
            if par_cls not in self.config_types:
                raise RuntimeError(f"Dependent Config Class {par_cls.__name__} not registered.")

        # Create object
        class_data = ConfigData(  # type: ignore[call-arg]
            data_cls=data_cls,
            interpolation_key=interpolation_key,
            conf_file=conf_file,
            conf_deps=conf_deps,
            default_conf=None,
            load_path=self._search_path(conf_file),
            overrides=None,
        )

        # Add to map
        self._add_conf_data(class_data)

    @classmethod
    def _get_config_class(cls, key: Union[str, Type]) -> Type:
        """
        Unpacks the key based on its type and value to find the appropriate
        config class.
        """
        inst = cls()
        data_cls = None

        if isinstance(key, str):
            if key in inst.name_map:
                data_cls = inst.name_map[key]
            elif key in inst.file_map:
                data_cls = inst.file_map[key]
            elif key in inst.key_map:
                data_cls = inst.key_map[key]
            else:
                RuntimeError(f"Config with key {key} not found.")
        else:
            data_cls = key

        return data_cls

    @classmethod
    def get(cls, key: Union[str, Type[T]]) -> T:
        """
        Retrieves an OmegaConf object for the associated dataclass type.

        Arguments:
            key: The dataclass or attrs class that represents the
                contents of the file.

                Note: this must have been previously registered.
        """
        return cls()._get(key)

    def _get(self, key: Union[str, Type[T]]) -> T:
        """
        See get for details
        """

        return self.config_types[self._get_config_class(key)].obj

    def __getitem__(self, key: Union[str, Type[T]]) -> T:
        """
        See get for details
        """
        return self._get(key)

    def __class_getitem__(cls, key: Union[str, Type[T]]) -> T:
        """
        See get for details
        """
        return cls.get(key)

    @classmethod
    def get_yaml(cls, key: Union[str, Type[T]]) -> str:
        """
        Returns the yaml string for a given config key.

        Arguments:
            key: The dataclass or attrs class that represents the
                contents of the file.

                Note: this must have been previously registered.
        """
        return cls()._get_yaml(key)

    def _get_yaml(self, key: Union[str, Type[T]]) -> str:
        """
        See get for details
        """

        return self.config_types[self._get_config_class(key)].yaml

    @classmethod
    def get_omegaconf(cls, key: Union[str, Type[T]]) -> T:
        """
        Returns the object for a given config key.

        Arguments:
            key: The dataclass or attrs class that represents the
                contents of the file.

                Note: this must have been previously registered.
        """
        return cls()._get_omegaconf(key)

    def _get_omegaconf(self, key: Union[str, Type[T]]) -> T:
        """
        See get_omegaconf for details
        """

        return self.config_types[self._get_config_class(key)].config

    @staticmethod
    def _get_argparser() -> argparse.ArgumentParser:
        """
        Get the arg parser for the conf_dir and run_mode options.
        """

        parser = argparse.ArgumentParser(add_help=False)

        # Config dir argument
        parser.add_argument(
            "--config-dir",
            action="append",
            default=[],
            type=Path,
            required=False,
            help="The directory containing all the config files used for this run. Can be given multiple times.",
        )

        # Run Mode Argument
        parser.add_argument(
            "--run-mode",
            action="append",
            default=[],
            type=Path,
            required=False,
            help="The mode in which this is being run, e.g. 'local', 'remote', or 'production'. Can be given multiple times.",
        )

        return parser

    @staticmethod
    def _invoke_args() -> List[Argument]:
        """
        Arguments to be used with an invoke Program class
        """

        return [
            Argument(
                name="config-dir",
                kind=str,
                default=[],
                help="The directory containing all the config files used for this run.",
            ),
            Argument(
                name="run-mode",
                kind=str,
                default=[],
                help="The mode in which this is being run, e.g. 'local', 'remote', or 'production'.",
            ),
        ]
