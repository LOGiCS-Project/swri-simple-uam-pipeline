from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic
from simple_uam.util.logging import get_logger
from simple_uam.fdm.parsing import parse_path_data, parse_fdm_dump
from .cli_wrapper import format_conversion
import json
import f90nml
import csv
from simple_uam.util.invoke import task, call

log = get_logger(__name__)

@task
def nml_to_json(ctx, input=None, output=None):
    """
    Convert a namelist, like `flightDynFast.inp` or `namelist.out`, into a
    json format.

    Arguments:
      input: The nml file to read from, if not provided reads from STDIN.
      output: The json file to write to, if not provided writes to STDOUT.
    """

    with format_conversion(input, output) as (in_fp, out_fp):
        json.dump(f90nml.read(in_fp), out_fp, indent=2, sort_keys=True)

@task
def json_to_nml(ctx, input=None, output=None):
    """
    Convert a json file into a namelist, like `flightDynFast.inp` or
    `namelist.out`.

    Arguments:
      input: The json file to read from, if not provided reads from STDIN.
      output: The nml file to write to, if not provided writes to STDOUT.
    """

    with format_conversion(input, output) as (in_fp, out_fp):
        f90nml.write(json.load(in_fp), out_fp)

@task
def path_to_csv(ctx, input=None, output=None):
    """
    Convert a path file, like `path.out`, into a csv file.

    Arguments:
      input: The path file to read from, if not provided reads from STDIN.
      output: The csv file to write to, if not provided writes to STDOUT.
    """

    with format_conversion(input, output) as (in_fp, out_fp):
        data, fieldnames = parse_path_data(in_fp.read())
        writer = csv.DictWriter(out_fp, fieldnames)
        writer.writeheader()
        writer.writerows(data)

@task
def path_to_json(ctx, input=None, output=None):
    """
    Convert a path file, like `path.out`, into a json file.

    Arguments:
      input: The path file to read from, if not provided reads from STDIN.
      output: The json file to write to, if not provided writes to STDOUT.
    """

    with format_conversion(input, output) as (in_fp, out_fp):
        data, fieldnames = parse_path_data(in_fp.read())
        json.dump(data, out_fp, indent=2, sort_keys=True)

@task
def fdm_to_json(ctx, input=None, output=None, permissive=False, strict=False):
    """
    Convert an FDM dump file (like `metrics.out`, `score.out`, and
    `fightDynFastOut.out`) into a json file.

    Arguments:
      input: The fdm dump file to read from, if not provided reads from STDIN.
      output: The json file to write to, if not provided writes to STDOUT.
      permissive: Will parse components of the file in smaller chunks, getting
        more out of a malformed file. Much slower than a non-permissive run.
      strict: Will not emit unparsed lines in 'blank_lines' blocks, instead
        will panic on unparsable inputs. Useful for debugging because it forces
        parse errors immediately instead of waiting for parse completion.
    """

    with format_conversion(input, output) as (in_fp, out_fp):
        data = parse_fdm_dump(in_fp.read(), permissive=permissive, strict=strict)
        json.dump(data, out_fp, indent=2, sort_keys=True)
