from .program import InvokeProg
from invoke import task, Collection, call
from typing import List

__all__: List[str] = ['InvokeProg','task','Collection','call']  # noqa: WPS410 (the only __variable__ we use)
