import shutil
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Union, List, Optional
from zipfile import ZipFile
import subprocess
import tempfile
import textwrap
import shutil
from urllib.parse import urlparse
import re
import platform
from attrs import define, field
from typing import Optional, Union, List, Dict

from .backup import archive_files
from ..config.service_config import ServiceConfig
from ..logging import get_logger

log = get_logger(__name__)


def _escape(arg):
    """
    Escapes input string for arg.
    """
    if not isinstance(arg,str):
        arg = str(arg)
    return arg # Assuming popen takes care of this for us right now.

def _exe_convert(val):
    if Path(val).is_absolute():
        pass
    elif shutil.which(val):
        val = shutil.which(val)
    return Path(val)

@define
class NssmService():
    """
    Class used to wrap the Non-Sucky Service Manager (nssm)
    """

    service_name : str = field()
    """ The name of the service. """

    display_name : str = field()
    """ The displayed name of the service. """

    description : str = field(
        converter=textwrap.dedent,
    )
    """ The displayed service description. """

    config : ServiceConfig = field()
    """ The user modifiable configuration settings for the service. """

    cwd : Path = field(
        converter=[Path, Path.resolve],
    )

    """ The working dir when running the service. """

    exe : Path = field(
        converter=_exe_convert,
    )
    """ The path to the app executable or the exe name. """

    @exe.validator
    def _exe_validator(self, attr, val):
        if platform.system() != 'Windows':
            return
            raise RuntimeError("NSSM service managment is Windows only.")
        elif val.is_absolute() and val.exists():
            pass
        elif (cwd / val).exists():
            pass
        else:
            raise RuntimeError(f"Could not find executable for {str(val)}")

    args : Union[str,List[str],None] = field(
        default=None,
    )
    """
    Arguments to use when starting the service.
    Windows quotation escapes are stupid: https://stackoverflow.com/questions/7760545/escape-double-quotes-in-parameter
    """

    # account : str = field(
    #     default="LocalSystem",
    # )
    # """
    # The user account to run the service with.
    # See [here](https://nssm.cc/commands) under "Native parameters" and
    # "ObjectName" for more info.
    # """

    # password : str = field(
    #     default="",
    # )
    # """
    # The password to the user account the service runs on.
    # See [here](https://nssm.cc/commands) under "Native parameters" and
    # "ObjectName" for more info.
    # """

    app_stop_method_skip : int = field(
        default=0,
    )
    """
    Which app stop methods to skip.
    See [here](https://nssm.cc/usage#shutdown) for more.
    """

    app_stop_console_delay : int = field(
        default=30000,
    )
    """
    Delay after attempting Control-C stop in ms.
    See [here](https://nssm.cc/usage#shutdown) for more.
    """

    app_stop_window_delay : int = field(
        default=30000,
    )
    """
    Delay after attempting window close stop in ms.
    See [here](https://nssm.cc/usage#shutdown) for more.
    """

    app_stop_thread_delay : int = field(
        default=30000,
    )
    """
    Delay after attempting thread kill stop in ms.
    See [here](https://nssm.cc/usage#shutdown) for more.
    """

    def install(self):
        """
        Install the service.
        """
        if platform.system() != 'Windows':
            raise RuntimeError("NSSM service managment is Windows only.")

        subprocess.run(
            ['nssm', 'install', self.service_name, str(self.exe)],
        )
        self.configure()

    def uninstall(self,confirm=True):
        """
        Uninstall the service.

        Arguments:
          confirm: show a GUI confirmation dialog.
        """
        if platform.system() != 'Windows':
            raise RuntimeError("NSSM service managment is Windows only.")

        conf_arg = ['confirm'] if confirm else []
        subprocess.run(
            ['nssm', 'remove', self.service_name, *conf_arg],
        )

    def gui_edit(self):
        """
        Opens the NSSM GUI editor.
        """
        if platform.system() != 'Windows':
            raise RuntimeError("NSSM service managment is Windows only.")
        subprocess.run(
            ['nssm', 'edit', self.service_name],
        )

    def configure(self):
        """
        Configures all the service parameters.
        """
        if platform.system() != 'Windows':
            raise RuntimeError("NSSM service managment is Windows only.")

        obj_name_args = None
        if self.config.password == "":
            obj_name_args = [self.config.account,'""']
        elif self.config.password == None:
            obj_name_args = self.config.account
        else:
            obj_name_args = [self.config.account, self.config.password]

        assignments = {
            "Application":str(self.exe),
            "AppDirectory":str(self.cwd),
            "AppParameters":self.args,
            "DisplayName":self.display_name,
            "Description":self.description,
            "Start": 'SERVICE_AUTO_START' if self.config.auto_start else 'SERVICE_DEMAND_START',
            "ObjectName":obj_name_args,
            "AppPriority":f"{self.config.priority}_PRIORITY_CLASS",
            "AppNoConsole":'0' if self.config.console else '1',
            "AppStopMethodSkip": self.app_stop_method_skip,
            "AppStopMethodConsole": self.app_stop_console_delay,
            "AppStopMethodWindow": self.app_stop_window_delay,
            "AppStopMethodThreads": self.app_stop_thread_delay,
            "AppThrottle": self.config.restart_throttle,
            "AppExit":['Default',self.config.exit_action],
            "AppRestartDelay":self.config.restart_delay,
            "AppRotateFiles":'1' if self.config.rotate_io else '0',
            "AppStdout": str(Path(self.config.stdout_file).resolve()),
            "AppStderr":  str(Path(self.config.stderr_file).resolve()),
            "Type": 'SERVICE_INTERACTIVE_PROCESS' if self.config.interactive else 'SERVICE_WIN32_OWN_PROCESS',
            "AppEvents Start/Pre": self.config.pre_hook,
            "AppEvents Exit/Post": self.config.post_hook,
        }

        log.info(
            "Creating Log Dirs",
            stdout =  str(Path(self.config.stdout_file).resolve()),
            stderr =  str(Path(self.config.stderr_file).resolve()),
        )
        Path(self.config.stdout_file).resolve().parent.mkdir(parents=True, exist_ok=True)
        Path(self.config.stderr_file).resolve().parent.mkdir(parents=True, exist_ok=True)

        for key, val in assignments.items():
            args = None

            key = key.split(" ")
            if val == None:
                args = ['nssm.exe', 'reset', self.service_name, *key]
            else:
                args=None
                if isinstance(val,list):
                    args = [_escape(a) for a in val]
                else:
                    args = [_escape(val)]
                args = ['nssm.exe', 'set', self.service_name, *key, *args]
            log.info(
                "Updating NSSM Config.",
                args=args,
            )
            subprocess.run(args)

    def start(self):
        """
        Start the service.
        """
        if platform.system() != 'Windows':
            raise RuntimeError("NSSM service managment is Windows only.")

        if self.config.redirect_io:
            stdout_dir = Path(self.config.stdout_file).parent
            stdout_dir.mkdir(parents=True, exist_ok=True)
            stderr_dir = Path(self.config.stderr_file).parent
            stderr_dir.mkdir(parents=True, exist_ok=True)

        subprocess.run(
            ['nssm', 'start', self.service_name],
        )

    def stop(self):
        """
        Stop the service.
        """
        if platform.system() != 'Windows':
            raise RuntimeError("NSSM service managment is Windows only.")

        subprocess.run(
            ['nssm', 'stop', self.service_name],
        )

    def restart(self):
        """
        Restart the service.
        """
        if platform.system() != 'Windows':
            raise RuntimeError("NSSM service managment is Windows only.")

        subprocess.run(
            ['nssm', 'restart', self.service_name],
        )

    def status(self):
        """
        Get service status.
        """
        if platform.system() != 'Windows':
            raise RuntimeError("NSSM service managment is Windows only.")

        process = subprocess.run(
            ['nssm', 'status', self.service_name],
        )
        return process.exitcode
