"""
A zip cache is a folder with a set of zip files that can be provided in
response to some key.
"""

import shutil
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic
from zipfile import ZipFile
from attrs import define, field
from copy import deepcopy
import subprocess
from filelock import FileLock, Timeout
from contextlib import contextmanager
import tempfile
import shutil
import hashlib
import json
import re
import heapq
import bz2
import base64
from enum import Enum, auto
from pathlib import Path

from .hash import stable_json_hash, stable_bytes_hash
from .glob import *
from ..logging import get_logger

log = get_logger(__name__)

K = TypeVar('K')

@define
class FileCache(Generic[K]):

    cache_dir : Path = field(
        converter=[Path, lambda x: x.resolve()],
        kw_only=True,
    )
    """
    Directory in which all the zip files are stored.
    """

    lock_dir : Path = field(
        default=None,
        kw_only=True,
    )
    """
    Directory in which all the lockfiles are stored.
    """

    temp_dir : Path = field(
        default=None,
        kw_only=True,
    )
    """
    Directory in where temporary folders for cache use are found.

    Should be on same drive as the cache dir.
    """

    prune_limit : int = field(
        default = 1000,
        kw_only=True,
    )
    """
    Number of cache items that should be remaining at the end of a prune
    cycle.
    """

    prune_trigger : int = field(
        default = 1100,
        kw_only=True,
    )
    """
    Threshold at which to prune the cache.
    """

    def __attrs_post_init__(self):
        if not self.lock_dir:
            self.lock_dir = Path(self.cache_dir / "locks").resolve()
        if not self.temp_dir:
            self.temp_dir = Path(self.cache_dir / "temp").resolve()

    def init_dirs(self):
        """
        Initialize various directories for the filecache.
        """

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def key_to_file(self, key : K):
        """
        Overloadable function that converts keys for this cache into filennames.

        Arguments:
          key: The key object for this cache.
        """

        raise NotImplementedError()

    def is_cache_entry(self, file_path : Path):
        """
        Overloadable function for determining if a file is a cache entry.

        Arguments:
          file_path: the path to the file to check.
        """

        raise NotImplementedError()

    def callback(self,
                 key : K,
                 output_file : Path,
                 **kwargs):
        """
        The default callback for generating an object in the cache if it's
        missing.

        Arguments:
          key: The key used to generated the callback.
          output_file: the file that the callback should write to.
          **kwargs: all other callbacks
        """

        raise NotImplementedError()

    def is_cached_file(self,
                       file_name : Union[str,Path]):
        """
        Is the file name in the cache?
        """

        cache_file_path = self.cache_dir / Path(file_name)

        return cache_file_path.exists()

    def is_cached(self, key : K):
        """
        Is the key in the cache?
        """

        return self.is_cached_file(self.key_to_file(key))

    def add_to_cache(self,
                     target_file : Union[str,Path],
                     file_name : Union[None,str,Path] = None,
                     key : Optional[K] = None,
                     copy : bool = True,
                     overwrite : bool = False):
        """
        Add a target file to the cache under a given name.

        Arguments:
          target_file: The file to add to the cache
          file_name: The name of the file, in the cache, to add. Should be
            ommitted if key is provided.
          key: The key to the cache entry, should be omitted if file_name is
            provided.
          copy: Should the target file be moved from the provided location
            instead of copied.
          overwrite: If the file is already in the cache should we move it?
        """

        self.init_dirs()

        target_file = Path(target_file)

        cache_file = None

        if file_name and key:
            raise RuntimeError(
                "add_to_cache can accept either a file_name arg or a key arg, "
                "not both."
            )
        elif file_name:
            cache_file = self.cache_dir / Path(file_name)
        elif key:
            cache_file = self.cache_dir / self.key_to_file(key)
        else:
            raise RuntimeError(
                "Exactly one of 'file_name' or 'key' arguments must be provided."
            )

        cache_file = cache_file.resolve()

        if cache_file.parent != self.cache_dir:
            raise RuntimeError(
                "Cache file name or key must be relative and not in a subdir."
            )

        with tempfile.TemporaryDirectory(dir=self.temp_dir) as tmp_dir:

            # Create a temorary copy if needed.
            if copy:
                target = Path(tmp_dir) / target_file.name
                shutil.copy2(target_file, target)
                target_file = target

            if cache_file.exists() and overwrite:
                log.info(
                    "Deleting existing cache file in favor of new.",
                    target_file=target_file,
                    cache_file=cache_file,
                )
                cache_file.unlink()

            if not cache_file.exists():
                log.info(
                    "Caching file",
                    target_file=target_file,
                    cache_file=cache_file,
                )
                shutil.move(target_file, cache_file) # assumes move is mostly atomic
            else:
                log.info(
                    "Cache already exists",
                    target_file=target_file,
                    cache_file=cache_file,
                )

        # Return the resulting filepath
        return cache_file


    @contextmanager
    def use_cache(self,
                  key : K,
                  force_gen : bool = False,
                  **kwargs):
        """
        Function that will get a context manager w/ manages access to the
        cachefile for the given key.

        Arguments:
          key: The key for the cache
          force_gen: Do we generate the cached item even if it already exists?
          **kwargs: Additional kwargs are passed to the callback.

        As stmt:
          A tuple where the first element is the cache item, and the second
          is whatever the callback returns, or None if it wasn't run.
        """

        self.init_dirs()

        cache_file_name = Path(self.key_to_file(key))

        cache_file_path = self.cache_dir / cache_file_name

        callback_return = None

        # Generate a new file if needed
        if force_gen or not self.is_cached_file(cache_file_name):
            with tempfile.TemporaryDirectory(dir=self.temp_dir) as tmp_dir:

                temp_target = Path(tmp_dir) / cache_file_name

                callback_return = self.callback(key, temp_target, **kwargs)

                if not temp_target.exists():
                    raise RuntimeError(
                        "Cache populating callback did not create a file at "
                        "the given location."
                    )

                cache_file_path = self.add_to_cache(
                    temp_target,
                    file_name=cache_file_name,
                    copy=False,
                    overwrite=True,
                )

        with tempfile.TemporaryDirectory(dir=self.temp_dir) as tmp_dir:

            tmp_file = Path(tmp_dir) / cache_file_name

            # We use hard links to create a "copy" of the file so deletions
            # and additions don't touch files in use.
            # This assumes that hardlinks are basically atomic.
            tmp_file.hardlink_to(cache_file_path)

            # Hand the temporary link & the result of the callback to the caller
            yield tuple([tmp_file, callback_return])

            # We let the tempdir context handle pruneing up the link we made.

    def entries(self):
        """
        List all the entries in the current cache.
        """

        self.init_dirs()

        for item in self.cache_dir.iterdir():
            if item.exists() and item.is_file() and self.is_cache_entry(item):
                yield item

    def prune_lock(self):
        prune_lockfile = self.lock_dir / "prune.lock"
        return FileLock(prune_lockfile)

    def prune(self,
              force = False,
              all = False):
        """
        If needed, prune the cache directory of the oldest entries over the
        prune limit.

        Arguments:
          force: Do a pruning even if the prune threshold hasn't been met.
          all: Prune all the items in the cache. Implies force.
        """

        if self.prune_limit <= 0:
            return

        self.init_dirs()

        force = force or all

        # get the entries in the cachedir
        now = datetime.now()
        total_results = 0
        results = list()
        for entry in self.entries():
            total_results += 1
            access_time = datetime.from_timestamp(entry.stat().st_atime)
            staletime = (now - access_time).total_seconds()
            results.append(tuple(staletime,result))

        # Short circuit if the there aren't enough items.
        if not force and total_results < self.prune_trigger:
            return

        # If we're not pruning everything up then only pick the oldest items
        # to remove.
        if not all:
            results = heapq.nlargest(
                total_results - self.prune_limit,
                results,
                key=lambda t: t[0],
            )

        try:
            # Presumably someone else is also pruning if there's a lock,
            # Just let them do the work, and move on.
            with self.prune_lock().acquire(blocking=False):
                for result in results:
                    # If a result got deleted before this point, that's fine.
                    results[1].unlink(missing_ok=True)
        except Timeout:
            pass
