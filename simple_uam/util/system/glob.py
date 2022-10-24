import re
import os
from typing import Optional, Dict, Union
import fnmatch
from pathlib import Path

from ..logging import get_logger

log = get_logger(__name__)

def split_glob(glob : str):
    """
    Splits a glob into component segments.
    """

    pos = 0
    end = len(glob)
    segments = list()

    while pos < end:

        wild = glob.find('*',pos,end)

        if wild < 0:
            segments.append(glob[pos:end])
            pos = end
        elif glob.startswith("**",wild,end):
            segments.append(glob[pos:wild])
            segments.append(glob[wild:wild + 2])
            pos = wild + 2
        elif glob.startswith("*",wild,end):
            segments.append(glob[pos:wild])
            segments.append(glob[wild:wild + 1])
            pos = wild + 1
        else:
            raise RuntimeError("Unreachable")

    return segments

def glob_regex_str(glob : str):
    """
    Converts a glob string to a regular expression that matches that glob.
    """

    regex = "^"

    wild_pat =  r'([^' + re.escape(os.sep) + re.escape(os.altsep) + r']+)'
    dubwild_pat = r'(.+)'

    for seg in split_glob(glob):
        if seg == "*":
            regex += wild_pat
        elif seg == "**":
            regex += dubwild_pat
        else:
            regex += re.escape(seg)

    regex += "$"

    return regex

def glob_regex(glob : str):
    """
    Converts a glob string to a regular expression that matches that glob.
    """
    return re.compile(glob_regex_str(glob), re.IGNORECASE)

def glob_match(glob : str, match : Optional[re.Match]):
    """
    Given a regex match will apply the result to the input glob pattern.

    The following should be true for all x and all y that matches x.
    ```
    glob_match(x,glob_regex(x).fullmatch(y)) == y
    ```

    Passes match failures through sliently.
    """

    if match == None:
        return None

    out = ""
    ind = 1
    for seg in split_glob(glob):
        if seg == "*" or seg == "**":
            out += match.group(ind)
            ind += 1
        else:
            out += seg

    return out

def glob_map(glob_in : str, glob_out : str, path : Union[str,Path]):
    """
    Given two glob with the same number of wildcards map a path from the
    input glob to the output glob.
    """

    path_in = path
    if isinstance(path, Path):
        path_in = str(path)

    match = re.fullmatch(glob_regex(glob_in), path_in)
    path_out = glob_match(glob_out, match)

    if path_out and isinstance(path, Path):
        return Path(path_out)
    else:
        return path_out

def apply_glob_mapping(glob_mapping : Dict[str,str],
                       cwd : Union[None,str,Path] = None,
                       files : Optional[List[Union[str,Path]]] = None):
    """
    This will take a glob mapping and get all matching files and their mappings
    , returning the resulting pairs when those input files exist.

    Will raise an error if there are any collisions when attempting to
    find a mapping.

    Arguments:
      glob_mapping: A dict of input and output glob pairs.
      cwd: The base dir the mappings are relative to, if not provided defaults
        to the current working dir.
      files: a list of filepaths to apply the glob mapping to, overrides cwd
        if it exists.
    """

    if not cwd:
        cwd = Path().cwd()
    cwd = Path(cwd)

    output = dict()

    for glob_in, glob_out in glob_mapping.items():

        glob_in = str(glob_in)
        glob_out = str(glob_out)

        files_in = None
        if files != None:
            files_in = fn_match.filter(files, glob_in)
        else:
            files_in = cwd.glob(glob_in)

        for result_in in files_in:
            result_out = Path(glob_map(glob_in, glob_out, result_in))

            if result_in in output and output[result_in] != result_out:
                raise RuntimeError(
                    f"Mismatched output files for the same input. "
                    f"`{str(result_in)}` is assigned to `{str(output[result_in])}` "
                    f"and `{str(result_out)}` when mapping sets of globs."
                )

            output[result_in] = result_out

    return output
