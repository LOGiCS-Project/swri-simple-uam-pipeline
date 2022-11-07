
from simple_uam.workspace.session import Session, session_op
from simple_uam.util.logging import get_logger
from simple_uam.worker import actor, message_metadata
from simple_uam.util.logging import get_logger
from simple_uam.util.config import Config, FDMCompileConfig
from simple_uam.util.system import backup_file, configure_file
from simple_uam.util.system.glob import apply_glob_mapping
from simple_uam.util.system.file_cache import FileCache
from simple_uam.util.system.text_dir import TDir
from contextlib import contextmanager, ExitStack
from simple_uam.fdm.compile.build_ops import gen_build_key
from simple_uam.fdm.compile.workspace import FDMCompileWorkspace
from simple_uam.fdm.compile.session import FDMCompileSession


from pathlib import Path, WindowsPath
from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic
from attrs import define, field

log = get_logger(__name__)

@define
class FDMBinCache(FileCache):
    """
    Cache for built FDM executables and libraries.

    Note: This contains the main function for actually building the fdm
    executables in the callback.
    """

    cache_dir : Path = field(
        default=Config[FDMCompileConfig].bin_cache_path,
        kw_only=True,
    )

    prune_limit : int = field(
        default = Config[FDMCompileConfig].bin_cache.max_count,
        kw_only=True,
    )
    """
    Number of cache items that should be remaining at the end of a prune
    cycle. if <= 0 no pruning will occur.
    """

    prune_trigger : int = field(
        kw_only=True,
    )
    """
    Threshold at which to prune the cache.
    """

    @prune_trigger.default
    def _default_prune_trigger(self):
        percent = round(self.prune_limit * 1.1)
        fixed = self.prune_limit + 5
        return max(percent, fixed)

    def key_to_file(self,
                    key : TDir):
        """
        The bin cache uses a key based on the reference key for the
        """

        normalized = gen_build_key(key)

        base = normalized.hash[0:8].hex('-')

        return Path(f"{base}.zip")

    def is_cache_entry(self, file_path : Path):

        return file_path.suffix == ".zip"

    def callback(self,
                 key: TDir,
                 output_file: Path,
                 user_metadata: Optional[object] = None,
                 force_autoreconf: bool = None,
                 force_configure: bool = None,
                 **kwargs,
    ):
        """
        This is the callback that actually generates the new fdm build object.

        Arguments:
          key: The TDir w/ all the sources we're using this .
          output_file: The location for the cache access to write to.
          user_metadata: An arbitrary JSON serializable object that will be included
            in 'metadata.json' under the 'user_metadata' field.
          force_autoreconf: do we run autoreconf in the woker? Implies force_configure.
          force_configure: do we run configure in the woker?
          **kwargs: additionals args to be passed to the workspace
        """

        with FDMCompileWorkspace(
                name="fdm-build",
                user_metadata=user_metadata,
                copy_zips=[output_file],
                **kwargs,
        ) as session:
            session.build_fdm(
                srcs=key,
                force_autoreconf=force_autoreconf,
                force_configure=force_configure,
            )

        return session

def has_compile_opts(srcs : Union[None, TDir, object] = None,
                     force_autoreconf : bool = False,
                     force_configure : bool = False,
                     force_make : bool = False):
    """
    Do we need to run the compilation phase of the pipeline given the
    provided inputs?

    Arguments:
      srcs: The TDir w/ all the sources we're using this .
      output_file: The location for the cache access to write to.
      user_metadata: An arbitrary JSON serializable object that will be included
        in 'metadata.json' under the 'user_metadata' field.
      force_autoreconf: do we run autoreconf in the woker? Implies force_configure.
      force_configure: do we run configure in the woker?
    """

    return srcs or force_autoreconf or force_configure or force_make

@contextmanager
def with_fdm_compile(srcs : Union[None,TDir,object],
                     metadata : Optional[object] =None,
                     force_autoreconf : bool = False,
                     force_configure : bool = False,
                     force_make : bool = False,
                     **kwargs,
):
    """
    A context manager which provides the current cached zip and closed session
    (if run) as a 'with as' return value.

    Skips actually performing the compilation if no inputs or options to force
    it are given.

    Performs normalization of key and init of parameters.

    Arguments:
      srcs: A TDir or compatible json representable that has the modified
        source files for the build.
      metadata: An arbitrary JSON serializable object that will be included
        in 'metadata.json' under the 'user_metadata' field.
      force_autoreconf: Force the autoreconf step in the build process
        (implies force_configure)
      force_configure: force configure step in build process
      force_make: force rebuild of the object even if it's in cache.
      **kwargs: Additional args to be passed to the FDM compile workspace
    """

    if srcs == None:
        pass
    elif srcs == []:
        srcs = None
    elif not isinstance(srcs,TDir):
        srcs = TDir.from_rep(srcs)

    key = None
    if srcs:
        key = gen_build_key(srcs)

    with ExitStack() as stack:

        cache_result = None

        use_cache = has_compile_opts(
            srcs=srcs,
            force_autoreconf=force_autoreconf,
            force_configure=force_configure,
            force_make=force_make,
        )

        if use_cache:
            cache_result = stack.enter_context(
                FDMBinCache().use_cache(
                    key,
                    force_gen=force_make,
                    user_metadata=metadata,
                    force_autoreconf=force_autoreconf,
                    force_configure=force_configure,
                    **kwargs,
                )
            )

        yield cache_result


def fdm_compile(srcs : Union[TDir,object],
                metadata : Optional[object] =None,
                force_autoreconf : bool = False,
                force_configure : bool = False,
                force_make : bool = False,
                **kwargs,
):
    """
    When run locally, on an appropriate worker node, this will build the FDM
    executable and gather the relevant dlls. This will, in other modules, be
    wrapped by an actor, as well local and remote tasks.

    Arguments:
      srcs: A TDir or compatible json representable that has the modified
        source files for the build.
      metadata: An arbitrary JSON serializable object that will be included
        in 'metadata.json' under the 'user_metadata' field.
      force_autoreconf: Force the autoreconf step in the build process
        (implies force_configure)
      force_configure: force configure step in build process
      force_make: force rebuild of the object even if it's in cache.
      **kwargs: Additional args to be sent to the fdm build workspace init.

    Returns:
      The metadata from either the build session or this particular cached
      session.
    """

    with with_fdm_compile(
            srcs=srcs,
            metadata=metadata,
            force_autoreconf=force_autoreconf,
            force_configure=force_configure,
            force_make=force_make,
            **kwargs,
    ) as (cached_zip, closed_session):

        # we're just using the cache since a new item wasn't created.
        if not closed_session:

            log.info(
                "Build with identical sources already exists in cache.",
                cached_zip = str(cached_zip),
            )

            with FDMCompileWorkspace(
                name="fdm-cache-lookup",
                user_metadata=metadata,
            ) as session:
                session.use_cached_build(cached_zip)
            result_session = session

        else:
            result_session = closed_session

    return result_session.metadata
