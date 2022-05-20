from invoke import Program

from ..config import Config


class InvokeProg(Program):
    """
    Can be used like Program from invoke, it just adds help text for the two
    arguments that the Config mechanism uses to extend the search path and
    add modes.
    """

    def core_args(self):
        return super(InvokeProg, self).core_args() + Config._invoke_args()
