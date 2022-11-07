import re
import os
from typing import Optional, Dict, Union, List
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

        split_chars = ['*', os.sep, os.altsep]
        splits = [glob.find(c,pos,end) for c in split_chars]
        splits = [s for s in splits if s >= 0]

        split = min(splits) if len(splits) > 0 else -1

        if split < 0:
            segments.append(glob[pos:end])
            pos = end
        elif glob.startswith("**",split,end):
            segments.append(glob[pos:split])
            segments.append(glob[split:split + 2])
            pos = split + 2
        elif any([glob.startswith(c,split,end) for c in split_chars]):
            segments.append(glob[pos:split])
            segments.append(glob[split:split + 1])
            pos = split + 1
        else:
            raise RuntimeError("Unreachable")

    # log.info(
    #     "Split glob into segments.",
    #     glob=glob,
    #     segments=segments,
    # )

    return segments

def glob_regex_str(glob : str):
    """
    Converts a glob string to a regular expression that matches that glob.
    """

    regex = "^"

    dir_pat = r'(?:' + re.escape(os.sep) + r'|' + re.escape(os.altsep) + r')'
    wild_pat =  r'([^' + re.escape(os.sep) + re.escape(os.altsep) + r']+)'
    dubwild_pat = r'(.+)'

    for seg in split_glob(glob):
        if seg == "*":
            regex += wild_pat
        elif seg == "**":
            regex += dubwild_pat
        elif seg == os.sep or seg == os.altsep:
            regex += dir_pat
        else:
            regex += re.escape(seg)

    regex += "$"

    # log.info(
    #     "Generated regex from glob.",
    #     glob=glob,
    #     regex=regex,
    # )

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

    groups = match.groups()
    groups = list(groups) if groups != None else list()

    out = ""
    ind = 0
    for seg in split_glob(glob):
        if seg == "*" or seg == "**":
            if ind > len(groups):
                break # short circuit to more useful error
            out += groups[ind]
            ind += 1
        else:
            out += seg

    if len(groups) != ind:
        raise RuntimeError(
            f"Attempting to apply glob '{glob}' to match '{str(match)}' "
            "fails because the number of wildcards in the glob ('*' and '**') "
            "isn't the same as the number of groups in the regex match."
        )

    # log.info(
    #     "Applying match group to glob.",
    #     glob=glob,
    #     groups=groups,
    #     match=match,
    #     out=out,
    #     ind=ind,
    # )

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

    # log.info(
    #     "Applied single glob mapping.",
    #     glob_in = glob_in,
    #     glob_out = glob_out,
    #     path_in = path_in,
    #     path_out = path_out,
    #     match = str(match),
    # )

    if path_out and isinstance(path, Path):
        path_out = Path(path_out)

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
        to the current working dir. Ignored if files is provided.
      files: a list of filepaths to apply the glob mapping to, overrides cwd
        if it exists.
    """

    if not cwd:
        cwd = Path().cwd()
    cwd = Path(cwd)

    output = dict()

    # log.info(
    #     "Applying a glob mapping to a set of files or directory.",
    #     mapping = {k: str(v) for k, v in glob_mapping.items()},
    #     cwd=str(cwd),
    #     files = str(files),
    # )

    for glob_in, glob_out in glob_mapping.items():

        glob_in = Path(glob_in)
        absolute_glob = files == None and glob_in.is_absolute()

        if absolute_glob and glob.is_relative_to(cwd):
                glob_in = glob_in.relative_to(cwd)
        elif absolute_glob:
            raise RuntimeError(
                f"Glob `{str(glob_in)}` must refer to subdirectories of "
                f"this call's cwd `{str(cwd)}` or be specified relative to it."
            )

        glob_in = str(glob_in)
        glob_out = str(glob_out)

        files_in = None
        if files != None:
            files_in = fnmatch.filter(files, glob_in)
        else:
            files_in = [f.relative_to(cwd) for f in cwd.glob(glob_in)]

        for result_in in files_in:

            result_out = glob_map(glob_in, glob_out, result_in)

            if result_out != None:
                result_out = Path(result_out)

            if result_in in output and output[result_in] != result_out:
                raise RuntimeError(
                    f"Mismatched output files for the same input. "
                    f"`{str(result_in)}` is assigned to `{str(output[result_in])}` "
                    f"and `{str(result_out)}` when mapping sets of globs."
                )

            # If we had an absolute path on the globs coming in, then we
            # want them on the globs coming out.
            if absolute_glob:
                result_in = cwd / result_in

            if result_out != None:
                output[result_in] = result_out

    more_files = ["..."] if files and len(files) > 5 else []
    more_output = {"...":"..."} if output and len(output) > 5 else dict()
    log.info(
        "Applied a glob mapping to a set of files or directory.",
        mapping = {str(k): str(v) for k, v in glob_mapping.items()},
        output = {str(k): str(v) for k, v in list(output.items())[:5]} | more_output,
        cwd=str(cwd),
        files=None if not files else [str(f) for f in files[:5]] + more_files,
    )

    return output
