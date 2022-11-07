"""
text_dirs are just special objects for storing a set of files in a
semi-readable, JSON-serializable way.

It's not efficient at all, but that's fine for now.
"""

import shutil
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Union, List, Optional, Dict
from zipfile import ZipFile
from attrs import define, field
from copy import deepcopy
import subprocess
import tempfile
import shutil
import hashlib
import json
import re
import bz2
import base64
from enum import Enum, auto
from pathlib import Path

from .hash import stable_json_hash, stable_bytes_hash
from .glob import *
from ..logging import get_logger

log = get_logger(__name__)

@define
class TDirEntry():

    kind : str = field()
    """
    The type of directory entry this is.
    """

    def to_rep(self) -> object:
        """
        Converts the DirEntry into a JSON encodable object.
        """

        raise NotImplementedError()

    @classmethod
    def from_rep(cls, rep: object):
        """
        Converts a JSON encoding of a DirEntry back into a python object.
        """

        if not isinstance(rep, dict):
            raise RuntimeError(
                "Rep for directory entry must be a dictionary."
            )

        if not 'kind' in rep:
            raise RuntimeError(
                "Rep for directory entry must have field 'kind'."
            )

        if rep['kind'] == 'file':
            return TFile.from_rep(rep)
        elif rep['kind'] == 'directory':
            return TDir.from_rep(rep)
        else:
            raise RuntimeError(
                f"Did not recognize kind '{rep['kind']}' for directory entry. "
                "Options are 'file' and 'directory'."
            )

    @property
    def hash(self) -> bytes:
        """
        Get the stable hash of this DirEntry.
        """

        raise NotImplementedError()

@define
class TFile(TDirEntry):
    """
    A text dir file with some contents in an encoding.
    """

    data : bytes = field()
    """
    The contents of this file as a raw bytes object.
    """

    compress_threshold : int = field(
        default= pow(2,20), # One Megabyte
    )
    """
    The size above which we start compressing and encoding file data
    in our JSON representation.
    """

    kind : str = field(
        default="file",
        init=False,
    )
    """
    The kind of directory entry this is.
    """

    def to_rep(self) -> object:
        """
        Converts the file data into a JSON encodable object.
        """

        encoding = None
        data = None

        if self.data.isascii() and len(self.data) < compress_threshold:
            encoding = "ascii"
            data = self.data
        else:
            encoding = "bz2_a85"
            compressed = bz2.compress(self.data)
            data = base64.a85encode(compressed)

        return dict(
            kind= self.kind,
            encoding=self.encoding,
            contents=self.contents,
        )

    @classmethod
    def from_rep(cls, rep : object):
        """
        Converts a JSON encoding of a file back into an in-memory bytestring.
        """

        if not isinstance(rep,dict):
            raise RuntimeError(
                "Expected rep of file to be a dictionary. "
                f"Instead found object of type {type(rep).__name__}."
            )

        if (not 'kind' in rep) or ('kind' != 'file'):
            raise RuntimeError(
                "Either could not find key 'kind' in rep or value of 'kind' "
                "wasn't 'file'."
            )

        if not ('encoding' in rep and 'contents' in rep):
            raise RuntimeError(
                "Rep for file must contain keys for both 'encoding' "
                "and 'contents'."
            )

        if len(rep) != 3:
            raise RuntimeError(
                "Representation for file must be a 3 item dict with keys "
                "'kind', 'encoding', and 'contents'."
            )

        if rep['encoding'] == "ascii":
            return cls(bytes(rep['contents']))
        elif rep['encoding'] == "bz2_a85":
            compressed = base64.a85decode(bytes(rep['contents']))
            return cls(bz2.decompress(compressed))
        else:
            raise RuntimeError(
                "Could not decode file with unknown encoding "
                f"'{rep['encoding']}'."
            )

    def write_file(self,
                   f : Union[str,Path]):
        """
        Write the file to disk at the give location.
        """
        f = Path(f).resolve()
        f.write_bytes(self.data)

    @classmethod
    def read_file(cls, f):
        """
        Read the file from disk at given location.
        """
        f = Path(f).resolve()
        return cls(f.read_bytes())

    @property
    def hash(self) -> bytes:
        """
        Get the stable hash of this file object.
        """
        return stable_bytes_hash(self.data)

@define
class TDir(TDirEntry):
    """
    A text dir directory with subdirs and files.
    """

    members : Dict[str,TDirEntry] = field(
        factory=dict
    )

    kind : str = field(
        default="directory",
        init=False,
    )
    """
    The kind of directory entry this is.
    """

    def to_rep(self) -> object:
        """
        Converts the directory data into a JSON ecodable object.
        """

        output = dict()

        for name, val in self.members.items():
            output[name] = val.to_rep()

        return dict(
            kind=self.kind,
            members=output,
        )

    @classmethod
    def from_rep(cls, rep: object):
        """
        Converts a JSON encoding of a directory back into a python object.
        """

        if not isinstance(rep, dict):
            raise RuntimeError(
                "Rep for directory must be a dict, instead found "
                f"object of type '{type(rep).__name__}'."
            )

        if 'kind' not in rep or rep['kind'] != "directory":
            raise RuntimeError(
                "Either the key 'kind' wasn't in the rep or its value wasn't "
                "'directory'."
            )

        if 'members' not in rep:
            raise RuntimeError(
                "Rep for directory must have key 'members'."
            )

        membs = dict()

        for name, memb_rep in rep['members']:
            membs[name] = TDirEntry.from_rep(memb_rep)

        return cls(members=membs)

    @property
    def hash(self) -> bytes:
        """
        Get the stable hash of this DirEntry.
        """

        memb_hash = {str(name): m.hash.hex() for name, m in self.members.items()}

        return stable_json_hash(memb_hash)

    @property
    def files(self) -> List[Path]:
        """
        A list of all the files in this text dir.
        """

        out = list()

        for name, dirent in self.members.items():
            if isinstance(dirent, TFile):
                out.append(Path(name))
            elif isinstance(dirent, TDir):
                out += [Path(name) / f for f in dirent.files]
            else:
                raise RuntimeError(
                    "Invalid member of directory with type "
                    f"'{type(dirent).__name__}'."
                )

        return out

    def get_dirent(self,
                   loc : Union[str,Path],
                   missing_ok : bool = False) -> Optional[TDirEntry]:
        """
        Get the dirent within this TDir

        Arguments:
          loc: The relative path to the directory entry we're looking for.
          missing_ok: If true just returns none if entry is missing.
            otherwise throws an error.
        """

        loc = Path(loc)

        if loc.is_absolute():
            raise RuntimeError(
                "Cannot use absolute path within text dir object."
            )

        parts = loc.parts
        current = parts[0]

        if current not in self.members:

            if missing_ok:
                return None

            raise RuntimeError(
                f"Could not find '{str(current)}' within current dir "
                f"while looking for '{str(f)}'."
            )

        step = self.members[current]

        if len(parts) == 1:
            return step
        elif isinstance(step, TDir):
            rest = Path(*parts[1:])
            return step.get_dirent(rest,missing_ok=missing_ok)
        else:

            if missing_ok:
                return None

            raise RuntimeError(
                f"Found file at '{current}' when trying to look up file at "
                f"'{str(loc)}'."
            )

    def __get_item__(self, key):
        """
        Gets a member dirent.
        """

        return self.members[key]

    def has_dirent(self,
                   loc : Union[str,Path]) -> bool:
        """
        Does the dirent already exist within this particular TDir.

        Arguments:
          loc: The relative path to the directory entry we're looking for.
        """
        return None != self.get_dirent(loc, missing_ok=True)

    def __contains__(self, key):
        """
        Alias for has_dirent.
        """
        return self.has_dirent(key)

    def add_dirent(self,
                   loc : Union[str,Path],
                   dirent : TDirEntry,
                   mkdir : bool = False,
                   overwrite : bool = False):
        """
        Adds a directory entry object to this directory at the provided
        location.

        Arguments:
          loc: The relative location within this directory that the dirent
            should be placed.
          dirent: The actual TDirEntry object to be placed at that location.
          mkdir: Should we make extra directories as needed to place the dirent?
            (default: False)
          overwrite: Should we overwrite a dirent that already exists when
            adding this one? (Default: False)
        """

        loc = Path(loc)

        if loc.is_absolute():
            raise RuntimeError(
                f"Cannot use absolute paths like '{str(loc)}' to describe "
                "locations within TDirs."
            )

        parts = loc.parts
        current = parts[0]

        if len(parts) == 1:
            if (current in self.members) and not overwrite:
                raise RuntimeError(
                    f"Dirent already exist at '{str(loc)}' cannot overwrite."
                )

            self.members[current] = dirent

        elif len(parts) >= 1:

            if (current not in self.members) and mkdir:
                self.members[current] = TDir()

            step = self.members[current]

            if current not in self.members:
                raise RuntimeError(
                    f"Could not find entry `{current}` in TDir."
                )
            elif not isinstance(step, TDir):
                raise RuntimeError(
                    f"Entry `{current}` in TDir has type "
                    f"'{type(step).__name__}' instead of "
                    "expected type 'TDir'."
                )

            rest = Path(*parts[1:])
            step.add_dirent(
                rest,
                dirent,
                mkdir=mkdir,
                overwrite=overwrite,
            )

    def add_file(self,
                 filepath : Union[str,Path],
                 dirloc : Union[str,Path],
                 mkdir : bool = False,
                 overwrite : bool = False):
        """
        Adds a directory entry object to this directory at the provided
        location.

        Arguments:
          filepath: The file system location of the file to be added.
          dirloc: The relative location within this directory that the file
            should be placed.
          mkdir: Should we make extra directories as needed to place the dirent?
            (default: False)
          overwrite: Should we overwrite a dirent that already exists when
            adding this one? (Default: False)
        """

        filepath = Path(filepath).resolve()

        self.add_dirent(
            loc=dirloc,
            dirent=TFile.read_file(filepath),
            mkdir=mkdir,
            overwrite=overwrite,
        )

    def add_files(self,
                  filemap : Dict[Union[str,Path],Union[str,Path]],
                  mkdir : bool = False,
                  overwrite : bool = False):
        """
        Adds a set of files to the directory.

        Arguments:
          filemap: A map from file system location of the file to be added to
            the relative location within this directory that the file
            should be placed.
          mkdir: Should we make extra directories as needed to place the dirent?
            (default: False)
          overwrite: Should we overwrite a dirent that already exists when
            adding this one? (Default: False)
        """

        for inp, out in filemap.items():

            self.add_file(
                filepath=inp,
                dirloc=out,
                mkdir=mkdir,
                overwrite=overwrite,
            )

    def __set_item__(self,key,value):
        """
        Alias for add_dirent with mkdir=True and overwrite=True.
        """
        self.add_dirent(key, value, mkdir=True, overwrite=True)

    def file(self, loc : Union[str,Path]) -> TFile:
        """
        Gets a file, with some name from the directory.

        Arguments:
          loc: The relative path to the file within this directory.
        """

        result = self.get_dirent(loc, missing_ok=False)

        if isinstance(result, TDir):
            raise RuntimeError(
                f"Found directory rather than file at '{str(loc)}' when "
                f"looking up file."
            )

        return result

    def write_dir(self,
                  loc : Union[None, str,Path] = None,
                  files : Optional[List[Union[str,Path]]] = None,
                  mapping : Optional[Dict[Union[str,Path],Union[str,Path]]] = None,
                  mkdir : bool = False,
                  overwrite : bool = False,):
        """
        Writes files from the directory to disk.

        Arguments:
          loc: The directory to write files into. (Default: cwd)
          files: The list of files (or globs) to copy into loc.
            All values must be relative paths. (Default: All files)
          mapping: Mapping from TDir file locations to output file locations.
            Overrides 'files' if provided. Keys must all be relative paths.
            If values are absolute paths they're taken as given.
            Otherwise they're moved relative to loc. (Default: None)
          mkdir: Do we make directories as needed for new files? (Default: False)
          overwrite : Can we overwrite existing files? (Default: False)
        """

        if not loc:
            loc = Path.cwd()
        loc = Path(loc).resolve()

        res_map = dict()

        # Manage files entries
        if files == None and not mapping:
            files = ["**"]
        elif files == None:
            files = []

        for f in files:

            f = str(f)

            if Path(f).is_absolute():
                raise RuntimeError(
                    f"File path '{str(f)}' in argument `files` is absolute, "
                    "only relative paths are allowed."
                )

            res_map[str(f)] = str(loc / f)

        # Manage mappings
        if not mapping:
            mapping = dict()

        for inp, out in mapping.items():

            inp = str(inp)
            out = Path(out)

            if Path(inp).is_absolute():
                raise RuntimeError(
                    f"Input path '{str(inp)}' in argument `mapping` is absolute, "
                    "only relative paths are allowed."
                )

            if not out.is_absolute():
                out = cwd / out

            res_map[str(inp)] = str(out)

        # Get actual input/output file pairs
        pairs = apply_glob_mapping(res_map, files=self.files)

        log.info(
            "Writing file pairs from TDir out to disk.",
            pairs = {str(k):str(v) for k, v in pairs.items()},
        )

        # And write them to disk
        for inp, out in pairs.items():

            in_file = self.file(inp)
            out = Path(out)

            if mkdir:
                out.parent.mkdir(parents=True, exist_ok=True)

            if not out.parent.exists():
                raise RuntimeError(
                    f"Folder '{str(out.parent)}' does not exist when trying to "
                    f"write file '{inp}' to '{str(out)}' when writing TDir."
                )

            if overwrite and out.exists():
                out.unlink()

            if out.exists():
                raise RuntimeError(
                    f"File '{str(out)}' already exists when trying to "
                    f"write file '{inp}' to '{str(out)}' when writing TDir."
                )

            in_file.write_file(out)

    @classmethod
    def read_dir(cls,
                 loc : Union[None, str,Path] = None,
                 files : Optional[List[Union[str,Path]]] = None,
                 mapping : Optional[Dict[Union[str,Path],Union[str,Path]]] = None):
        """
        Reads files from disk to the directory entry.

        Arguments:
          loc: The directory to read files from. (Default: cwd)
          files: The list of files (or globs) to copy into loc.
            All paths must be relative to loc. (Default: All files under loc)
          mapping: Mapping from file system locations to TDir file locations.
            Overrides 'files' if provided. Both keys and values must be
            relative to loc. (Default: None)
        """

        if not loc:
            loc = Path.cwd()
        loc = Path(loc).resolve()

        res_map = dict()

        # Manage files entries
        if files == None and not mapping:
            files = ["**"]
        elif files == None:
            files = []

        for f in files:

            f = str(f)

            if Path(f).is_absolute():
                raise RuntimeError(
                    f"File path '{str(f)}' in argument `files` is absolute, "
                    "only relative paths are allowed."
                )

            res_map[str(f)] = str(f)

        # Manage mappings
        if not mapping:
            mapping = dict()

        for inp, out in mapping.items():

            inp = Path(inp)
            out = Path(out)

            if inp.is_absolute():
                raise RuntimeError(
                    f"Inp path '{str(inp)}' in argument `mapping` is absolute, "
                    "only relative paths are allowed."
                )

            if out.is_absolute():
                raise RuntimeError(
                    f"Output path '{str(out)}' in argument `mapping` is absolute, "
                    "only relative paths are allowed."
                )

            res_map[str(inp)] = str(out)


        log.info(
            "Reading files into TDir.",
            mapping={k: str(v) for k,v in res_map.items()},
            files= [str(f) for f in files] if files else None,
            loc=str(loc),
        )

        # Get the full map from input to putput files
        pairs = apply_glob_mapping(res_map, loc)

        # Make sure the input paths are relative to loc
        pairs = {loc / k: v for k, v in pairs.items()}

        out = cls()
        out.add_files(pairs, mkdir=True, overwrite=False)
        return out

    @property
    def empty(self):
        """
        Is this directory empty?
        """

        return len(self.members) == 0

    def difference(self, other : 'TDir'):
        """
        Produces a new TDir that has the directory entries of self without any
        found in other.

        Note: A file in self colliding with a dir in other won't be included.

        Arguments:
          other: Other TDir which determines what entries to remove.
        """

        out = TDir()

        for name, dirent in self.members.items():
            other_dirent = other.members.get(name)

            # Item isn't in other, include
            if name not in other.members:
                out.add_dirent(name, deepcopy(dirent))

            # Item is dir in both, take difference of dirs
            elif isinstance(dirent,TDir) and isinstance(other_dirent,TDir):
                out_dirent = dirent.difference(other_dirent)
                if not out_dirent.empty:
                    out.add_dirent(name, out_dirent)

        return out

    def overlay(self, other : 'TDir'):
        """
        Produces a new TDir that is identical to self except when a dirent
        also exists in other, in which case it uses the dirent from other

        Note: Directory / File collisions are resolved in favor of other.

        Arguments:
          other: The other TDir whose entries are used when there's overlap.
        """

        out = TDir()

        for name, dirent in self.members.items():
            other_dirent = other.members.get(name)

            # Item isn't in other, include unchanged
            if name not in other.members:
                out.add_dirent(name, deepcopy(dirent))

            # Item is dir in both, take overlay of dirs
            elif isinstance(dirent,TDir) and isinstance(other_dirent,TDir):
                out_dirent = dirent.overlay(other_dirent)
                if not out_dirent.empty:
                    out.add_dirent(name, out_dirent)

            # Item of different types use dirent from other
            else:
                out.add_dirent(name, deepcopy(other_dirent))

        return out

    def intersection(self, other : 'TDir'):
        """
        Produces a new TDir that composed of those directory entries that
        are also found in other.

        Note: Directory / File collisions are resolved in favor of other.

        Arguments:
          other: The other TDir whose entries are checked against.
        """

        out = TDir()

        for name, dirent in self.members.items():
            other_dirent = other.members.get(name)

            # Item is dir in both, take overlay of dirs
            if isinstance(dirent,TDir) and isinstance(other_dirent,TDir):
                out_dirent = dirent.intersection(other_dirent)
                if not out_dirent.empty:
                    out.add_dirent(name, out_dirent)

            # otherwise take other
            else:
                out.add_dirent(name, deepcopy(other_dirent))

        return out

    def union(self, other : 'TDir'):
        """
        Produces new TDir with all the entries of self and other.

        Note: Directory / File collisions are resolved in favor of other.

        Arguments:
          other: The other TDir whose entries are used when there's overlap.
        """

        out = TDir()

        keys = set(self.members)
        keys.update(set(other.members))

        for name in keys:
            dirent = self.members.get(name)
            other_dirent = other.members.get(name)

            # Item is dir in both, take union of dirs
            if isinstance(dirent,TDir) and isinstance(other_dirent,TDir):
                out_dirent = dirent.union(other_dirent)
                if not out_dirent.empty:
                    out.add_dirent(name, out_dirent)

            # Item in other, use that
            elif other_dirent:
                out.add_dirent(name, deepcopy(other_dirent))

            # Item in self, use that
            else:
                out.add_dirent(name, deepcopy(dirent))

        return out

    def is_subsumed_by(self, other : 'TDir'):
        """
        Does every entry in self exist in other?

        Arguments:
          other: The other TDir which is being checked against
        """

        out = TDir()

        for name, dirent in self.members.items():
            other_dirent = other.members.get(name)

            # Item is dir in both, if not subsumed, propagate
            if isinstance(dirent,TDir) and isinstance(other_dirent,TDir):
                if not dirent.is_subsumed_by(other_dirent):
                    return False

            # item not subsumed
            elif not other_dirent:
                return False

        # All items exist
        return True
