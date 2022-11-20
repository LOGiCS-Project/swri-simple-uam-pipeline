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
from type import TracebackType
from pathlib import Path
from attrs import define, field, asdict
from copy import deepcopy
import json
import traceback
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

    def __init__(cls,
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

        def default_converter(val):
            try:
                return json.loads(json.dumps(val))
            except Exception:
                pass

            try:
                return str(val)
            except Exception:
                pass

            return repr(val)

        converter = local_converter if local_converter else default_converter

        output = dict(
            filename = self.filename,
            lineno = self.lineno,
            name = self.name,
        )

        if self.line:
            output['line'] = self.line,

        if self.locals:
            output['locals'] = {k: converter(v) for k,v in self.locals.items()}

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

        output = deepcopy(exc.to_rep())

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
                    ExcFrame.from_frame_summry(frame_summary)
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
    e_trace = ExcTrace(e_box,show_locals=show_locals)
    return e_trace.to_rep(local_converter=local_converter)
