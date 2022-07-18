import structlog
from structlog.dev import ConsoleRenderer, _pad
from structlog._frames import _format_exception
from structlog.types import (
    EventDict,
    ExceptionFormatter,
    ExcInfo,
    Protocol,
    WrappedLogger,
)

from io import StringIO
from typing import Any, Iterable, Optional, TextIO, Type, Union
# from rich.console import Console
import textwrap
import os
import sys

__all__ = ['get_logger']

def strip_empty_lines(s: str) -> str:
    lines = s.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return '\n'.join(lines)

def multiline(s: str) -> bool:
    return len(s.splitlines()) > 1

def try_dent(inp : str,
             indent: str = "  ",
             pad_len : Optional[int] = None) -> str:
    """
    Will try to dedent and clean edges of input string, will indent if
    result is more than a single line.
    """

    inp = strip_empty_lines(inp)
    inp = textwrap.dedent(inp)
    if multiline(inp):
        inp = textwrap.indent(inp, indent)
    if pad:
        inp = "\n".join([_pad(i,pad_len) for i in inp.splitlines()])
    return inp

class CustomRenderer(ConsoleRenderer):
    """
    Wraps the console renderer to add a bit more whitespace and formatting.
    """

    def __call__(
        self,
        logger: WrappedLogger,
        name: str,
        event_dict: EventDict
    ) -> str:

        sio = StringIO()

        prompt = ""
        ts = event_dict.pop("timestamp", None)
        if ts is not None:
            prompt += (
                # can be a number if timestamp is UNIXy
                self._styles.timestamp
                + str(ts)
                + self._styles.reset
                + " "
            )
        level = event_dict.pop("level", None)
        if level is not None:
            prompt += (
                "["
                + self._level_to_color.get(level, "")
                + _pad(level, self._longest_level)
                + self._styles.reset
                + "] "
            )

        # force event to str for compatibility with standard library
        event = event_dict.pop("event", None)
        if not isinstance(event, str):
            event = str(event)

        event = try_dent(event)

        if multiline(event):
            prompt += _pad("", self._pad_event)
            event = "\n\n" + self._styles.bright + event
            event += self._styles.reset
        else:
            prompt += self._styles.bright
            prompt += _pad(event, self._pad_event)
            prompt += self._styles.reset
            event = None

        sio.write(prompt)

        logger_name = event_dict.pop("logger", None)
        if logger_name is None:
            logger_name = event_dict.pop("logger_name", None)

        if logger_name is not None:
            sio.write(
                "["
                + self._styles.logger_name
                + self._styles.bright
                + logger_name
                + self._styles.reset
                + "] "
            )

        sio.write(event)

        stack = event_dict.pop("stack", None)
        exc = event_dict.pop("exception", None)
        exc_info = event_dict.pop("exc_info", None)

        event_dict_keys: Iterable[str] = event_dict.keys()
        if self._sort_keys:
            event_dict_keys = sorted(event_dict_keys)

        dict_vals = list()
        console = Console()

        for key in event_dict_keys:

            pretty_key = (
                self._styles.kv_key
                + key
                + self._styles.reset
                + "="
            )

            with console.capture() as capture:
                console.print(self._repr(event_dict[key]))
            pretty_val = try_dent(capture.get())

            if multiline(pretty_val):
                dict_vals.append(
                    pretty_key + "\n" + textwrap.indent(pretty_val,"  ")
                )
            else:
                dict_vals.append(
                    pretty_key + " " + pretty_val
                )

        sio.write("\n\n")
        sio.write("\n\n".join(dict_vals))

        if stack is not None:
            sio.write("\n" + stack)
            if exc_info or exc is not None:
                sio.write("\n\n" + "=" * 79 + "\n")

        if exc_info:
            if not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()

            self._exception_formatter(sio, exc_info)
        elif exc is not None:
            if self._exception_formatter is not plain_traceback:
                warnings.warn(
                    "Remove `format_exc_info` from your processor chain "
                    "if you want pretty exceptions."
                )
            sio.write("\n" + exc)

        return sio.getvalue()

def get_logger(name: str):
    logger = structlog.get_logger(name)
    return structlog.wrap_logger(
        logger,
        processors=[
        ]
    )
