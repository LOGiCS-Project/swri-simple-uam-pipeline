"""
Some formatting and helpers for working with exceptions.

Heavily inspired by / cribbed from: https://rich.readthedocs.io/en/latest/_modules/rich/traceback.html#Traceback
"""

# from simple_uam.util.system import Rsync
# import simple_uam.util.system.backup as backup
# from simple_uam.util.system.git import Git
# from simple_uam.worker import actor, message_metadata
# from attrs import define,field
# from filelock import Timeout, FileLock
# from functools import wraps
# from datetime import datetime
# import subprocess
# import platform
# import os
# import uuid
# import socket
# import re
# import json

from typing import List, Tuple, Dict, Optional, Union, Any, Type, Callable
from types import TracebackType
from pathlib import Path
from attrs import define, field
import attrs
import dataclasses
from copy import deepcopy
import ast
import json
import traceback
import sys
from inspect import ismodule
from simple_uam.util.logging import get_logger

log = get_logger(__name__)

@define
class ExcBox():
    """
    A canonical container for an exception split into its components.

    Arguments:
      *exc: A single exception to box, mutually exclusive with
        following args.
      typ: The type of the exception.
      val: The value of the exception.
      tb: The traceback of the exception.
    """

    typ : Type[BaseException]
    val  : BaseException
    tb   : Optional[TracebackType] = None

    def to_rep(self):
        """
        Converts this ExcBox to a json serializable object.
        This is a pretty printer for human use more than a serializer.
        """

        return dict(
            type = self.typ.__name__,
            value = traceback.format_exception_only(self.typ, self.val),
            traceback = traceback.format_tb(self.tb),
        )

    def __init__(self,
                 *excs,
                 typ=None,
                 val=None,
                 tb=None):

        split_exc = typ or val or tb
        some_exc = len(excs) > 0
        one_exc = len(excs) == 1

        if split_exc == some_exc:
            raise RuntimeError(
                "Can only provide positional arg or kw args, "
                "not both or neither."
            )
        elif not split_exc and not one_exc:
            raise RuntimeError(
                "Can only log a single exception at a time."
            )
        elif one_exc:
            exc = excs[0]
            if isinstance(exc, ExcBox):
                self.__attrs_init__(
                    typ=exc.typ,
                    val=exc.val,
                    tb=exc.tb,
                )
            else:
                self.__attrs_init__(
                    typ=type(exc),
                    val=exc,
                    tb=exc.__traceback__,
                )
        elif split_exc:
            self.__attrs_init__(
                typ=typ or type(val),
                val=val,
                tb=tb or val.__traceback__,
            )
        else:
            raise RuntimeError("Unreachable")

def default_converter(val):
    """
    Converts an input value into a json rep in a maximally permissive way.
    The goal is to produce a useful debugging output, not consistency or
    correctness.

    Tries the following things to produce useful output:
      - Checks if val is too large, returns placeholder if so.
      - Tries round-tripping the input through a json parser, returns result.
      - Tries parsing the string as if it's json, returns result.
      - Tries parsing string as if it's a python literal, continues.
      - If val is a string, return that directly.
      - Unpacks an attrs dataclass with asdict, continues.
      - Unpacks a normal dataclass with asdict, continues.
      - Recurses into dictionaries converting each item.
      - Recurses into lists and iterables converting each item.
      - Returns the `str(_)` representation of the input.
      - Returns the `repr(_)` of the input.

    TODO :: This is all a bit redundant since traceback saves the locals as
            strings. Most of the options are not reachable. The correct way to
            solve this is to use the `ast` module to parse the input and render
            a version of that into a structure.

    Arguments:
      val: Input to convert into a JSON object.
    """

    serializable = False

    # short circuit basic primitive types
    small_prim_types = [int, float]
    if any([isinstance(val,t) for t in small_prim_types]):
        return val

    # unpack json serializable objects
    skip_roundtrip_types = [str, dict, list, bytes, bytearray, range]
    if not any([isinstance(val,t) for t in skip_roundtrip_types]):
        try:
            val = json.loads(json.dumps(val, sort_keys=True))
            serializable = True
        except Exception:
            pass

    # loading json strings
    if isinstance(val, str):
        try:
            val = json.loads(val)
            serializable = True
        except Exception:
            pass

    # checking if str input is a parsable python literal
    if isinstance(val, str):
        try:
            val = ast.literal_eval(val)
        except Exception:
            pass

    # Unpack attrs classes if given
    try:
        val = attrs.asdict(val)
    except Exception:
        pass

    # Unpack dataclasses if given
    try:
        val = dataclasses.asdict(val)
    except Exception:
        pass

    # skip objects that are too large
    size = sys.getsizeof(val)
    max_size = 5 * 1024 # 5 kb
    if not isinstance(val,str) and size > max_size:
        val = {
            'err_placeholder': f"Input variable too large, eliding from output.",
            'var_size': size,
        }
        serializable = True

    # Recursively unpack dicts
    if isinstance(val, dict):
        val = {str(k):default_converter(v) for k,v in val.items()}
        serializable = True

    # recursively unpack lists and other iterables
    skip_list_types = [str, bytes, bytearray,range]
    if not any([isinstance(val,t) for t in skip_list_types]):
        try:
            val = [default_converter(v) for v in val]
            serializable = True
        except Exception:
            pass

    # Fallback to string rep or repr
    if not serializable:
        try:
            val = str(val)
        except Exception:
            val = repr(val)

    # Splits a string into lines for easier readability. Leaves it as a string
    # if there's no line breaks (as opposed to turning it into a list).
    def split_if(s):
        out = s.splitlines(keepends=True)
        if len(out) > 1:
            return out
        else:
            return s

    # Trim long output string
    max_size = 5 * 1024 # 5 kb
    if isinstance(val, str) and len(val) > max_size:
        val = {
            'err_placeholder': "Output string too long, trimming to length.",
            'string_prefix': split_if(val[:max_size]),
            'str_length': len(val),
        }
        serializable = True
    elif isinstance(val, str):
        return split_if(val)
    else:
        return val

@define
class ExcFrame():
    """
    A frame of an exception.
    """

    filename: str
    lineno: int
    name: str
    line: Optional[str] = None
    locals: Optional[Dict[str,Any]] = None

    def to_rep(self,
               local_converter : Optional[Callable]):
        """
        Converts this exc_frame to a json_serializable object.

        Arguments:
          local_converter: Function to convert local variable values into
            JSON representable objects. (Default: Attempts to convert via
            json.dumps/json.loads, then str, then repr)
        """

        converter = local_converter if local_converter else default_converter

        output = dict(
            filename = self.filename,
            lineno = self.lineno,
            name = self.name,
        )

        if self.line:
            output['line'] = self.line,

        if self.locals:
            output['locals'] = dict()

            for k,v in self.locals.items():

                # print(f"Converting local '{k}' of type {type(v)}.")
                output['locals'][k] = converter(v)

        return output

    @classmethod
    def from_frame_summary(cls,
                           frame_summary : traceback.FrameSummary,
                           filter_locals : Optional[Callable] = None):
        """
        Unwraps a traceback.FrameSummary into a more convenient representation.

        Expects a framesummary that's been unpacked by StackSummary.extract
        like this:

        ```py
        tb = err.__traceback__
        tbs = traceback.walk_tb(tb)
        frame_sums = traceback.StackSummary.extract(tbs, ...)
        ```

        Arguments:
          frame_summary: The FrameSummary object to decode
          filter_locals: Provide a function (name -> val -> bool) to filter
            out any locals we don't want to preserve. (Default: modules and
            dunders are ignored.)
        """

        def default_filter(name, val):
            return not ("__" in name or ismodule(val))

        filter_locals = filter_locals if filter_locals else default_filter

        locs = {
            k:deepcopy(v) for k,v in frame_summary.locals.items() if filter_locals(k,v)
        }

        return cls(
            filename = frame_summary.filename,
            lineno = frame_summary.lineno,
            name = frame_summary.name,
            line = frame_summary.line,
            locals = locs if locs else None,
        )

@define
class ExcSyntax():
    """
    Syntax Error specific info.
    """

    offset: int
    filename: str
    line: str
    lineno: int
    msg: str

    def to_rep(self):
        """
        Converts this syntax error into a json representable object.
        """

        return dict(
            offset= self.offset,
            filename = self.filename,
            line = self.line,
            lineno = self.lineno,
            msg = self.msg,
        )

    @classmethod
    def from_exc(cls,
                 exc : 'ExcBox'):
        """
        Will gather syntax error specific info from a syntax error.
        Returns None if not given syntax error.

        Arguments:
          exc: The exception box to use.
        """

        exc = ExcBox(exc)

        if not isinstance(exc.val, SyntaxError):
            return None

        return cls(
            offset=exc.val.offset or 0,
            filename=exc.val.filename or "??",
            lineno=exc.val.lineno or 0,
            line=exc.val.text or "",
            msg=exc.val.msg,
        )

@define
class ExcStack():
    """
    A single exception frame on the stack.
    """
    exc : 'ExcBox'
    syntax_error: Optional[ExcSyntax] = field()

    @syntax_error.default
    def _default_syntax_error(self):
        return ExcSyntax.from_exc(self.exc)

    is_cause: bool = False
    frames: List[ExcFrame] = field(factory=list)

    def to_rep(self,
               local_converter : Optional[Callable] = None):
        """
        Converts this ExcStack to a json serializable object.

        Arguments:
          local_converter: Function to convert local variable values into
            JSON representable objects. (Default: Attempts to convert via
            json.dumps/json.loads, then str, then repr)
        """

        output = deepcopy(self.exc.to_rep())

        if self.syntax_error:
            output['syntax_error'] = self.syntax_error.to_rep()

        output['is_cause'] = self.is_cause

        if self.frames:

            output['stack_frames'] = [
                f.to_rep(local_converter=local_converter) for f in self.frames
            ]

        return output

@define
class ExcTrace():
    """
    A full trace coming from an exception.
    """
    stacks : List[ExcStack] = field(factory=list)

    def to_rep(self,
               local_converter : Optional[Callable] = None):
        """
        Converts this ExcTrace to a json serializable object.

        Arguments:
          local_converter: Function to convert local variable values into
            JSON representable objects. (Default: Attempts to convert via
            json.dumps/json.loads, then str, then repr)
        """

        return [s.to_rep(local_converter=local_converter) for s in self.stacks]

    @classmethod
    def from_exc(cls,
                 exc: ExcBox,
                 show_locals: bool = False):
        """
        Creates a trace object from a ExcBox.

        Arguments:
          exc: The ExcBox that we're decoding
          show_locals: Do we try to capture the assorted locals in each frame?
        """

        trace = cls()
        is_cause = False

        while exc != None:

            stack = ExcStack(
                exc=exc,
                is_cause=is_cause,
            )

            frames = list(traceback.walk_tb(exc.tb))

            frame_summaries = traceback.StackSummary.extract(
                frames,
                lookup_lines=True,
                capture_locals = show_locals,
            )

            for frame_summary in frame_summaries:

                stack.frames.append(
                    ExcFrame.from_frame_summary(frame_summary)
                )

            cause = getattr(exc.val, "__cause__", None)
            context = getattr(exc.val, "__context__", None)
            if getattr(exc.val, "__suppress_context__", False):
                context = None

            if cause:
                exc = ExcBox(cause)
                is_cause = True
            elif context:
                exc = ExcBox(context)
                is_cause = False
            else:
                exc = None

            trace.stacks.append(stack)

        return trace

def contextualize_exception(*excs,
                            exc_type=None,
                            exc_val=None,
                            exc_tb=None,
                            show_locals=True,
                            local_converter : Optional[Callable] = None):
    """
    Produces a json serializable object that gathers its context, including
    stack frames, local variables, and other data.

    Arguments:
      *excs: A single exception to contextualize.
      exc_type: The type of the exception.
      exc_val: The value of the exception.
      exc_tb: The traceback of the exception.
      show_locals: Should we gather local variable information for the stack
        stack frames?
      local_converter: Function to convert local variable values into
        JSON representable objects. (Default: Attempts to convert via
        json.dumps/json.loads, then str, then repr)
    """

    e_box = ExcBox(*excs,typ=exc_type,val=exc_val,tb=exc_tb)
    e_trace = ExcTrace.from_exc(e_box,show_locals=show_locals)
    return e_trace.to_rep(local_converter=local_converter)
