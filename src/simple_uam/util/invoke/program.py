from invoke import Program
import sys
from ..config import Config


class InvokeProg(Program):
    """
    Can be used like Program from invoke, it just adds help text for the two
    arguments that the Config mechanism uses to extend the search path and
    add modes.

    Has some fixes that make executables easier to use as pdm tool scripts.
    """

    def core_args(self):
        return super(InvokeProg, self).core_args() + Config._invoke_args()

    def run(self, argv=None, exit=True):
        # Special case for how pdm seems to do things when calling as a script.
        # The args in the pyproject.toml are passed directly while command
        # line args are found in sys.args after a '-c' flag.
        if (isinstance(argv,list)
            and argv[0].startswith("pdm run")
            and sys.argv[0] == '-c'):
            argv = argv + sys.argv[1:]
        return super(InvokeProg, self).run(argv,exit)
