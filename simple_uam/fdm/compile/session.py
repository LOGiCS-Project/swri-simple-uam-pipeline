
from simple_uam.workspace.session import Session, session_op
from simple_uam.util.logging import get_logger
from simple_uam.util.config import Config, FDMCompileConfig
from simple_uam.util.system import backup_file, configure_file
from simple_uam.util.system.glob import apply_glob_mapping
import simple_uam.util.system.backup as backup
import simple_uam.fdm.compile.build_ops as ops
from zipfile import ZipFile
import tempfile
from attrs import define,field
from simple_uam.worker import actor
from time import sleep
import shutil
import json
from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic
import csv
from pathlib import Path

log = get_logger(__name__)

@define
class FDMCompileSession(Session):
    """
    A workspace session specialized to the direct2cad workflow.
    """

    copy_bins : List[Union[str, Path]] = field(
        factory=list,
        kw_only=True,
    )
    """
    Do we copy the binaries generated from this session into some location?
    If so where?
    """

    copy_zips :  List[Union[str, Path]] = field(
        factory=list,
        kw_only=True,
    )
    """
    Do we copy the output archives from this session into some locations?
    if so where?
    """

    cached_zip : Union[None,str,Path] = field(
        default=None,
        kw_only=True,
    )
    """
    A cached zip file to use when constructing the final output zip.
    If provided, any existing build state will be ignored, except for
    'metadata.json'. Usually set with the "use cached zip" function.
    """

    @session_op
    def run_autoreconf(self,
                       timeout = None):
        """
        Runs autoreconf w/in the current workspace.

        Arguments:
          timeout: Amount of time to wait for autoreconf to finish (default
            from configuration file)
        """

        if timeout == None:
            timeout = Config[FDMCompileConfig].autoreconf_timeout

        log.info(
            "Starting autoreconf",
            workspace=self.number,
            work_dir=str(self.work_dir),
        )

        process = ops.run_autoreconf(
            cwd=self.work_dir,
            timeout=timeout,
            run_cmd=self.run,
        )

        process.check_returncode()

        log.info(
            "Finished autoreconf",
            workspace=self.number,
            work_dir=str(self.work_dir),
        )

    @session_op
    def run_configure(self,
                      timeout = None):
        """
        Runs configure w/in the current workspace.

        Arguments:
          timeout: Amount of time to wait for configure to finish (default
            from configuration file)
        """

        if timeout == None:
            timeout = Config[FDMCompileConfig].configure_timeout

        log.info(
            "Starting configure",
            workspace=self.number,
            work_dir=str(self.work_dir),
        )

        process = ops.run_configure(
            cwd=self.work_dir,
            timeout=timeout,
            run_cmd=self.run,
        )

        process.check_returncode()

        log.info(
            "Finished configure",
            workspace=self.number,
            work_dir=str(self.work_dir),
        )

    @session_op
    def run_make(self,
                 timeout= None):
        """
        Runs make w/in the current workspace.

        Arguments:
          timeout: Amount of time to wait for make to finish (default
            from configuration file)
        """

        if timeout == None:
            timeout = Config[FDMCompileConfig].make_timeout

        log.info(
            "Starting make",
            workspace=self.number,
            work_dir=str(self.work_dir),
        )

        process = ops.run_make(
            cwd=self.work_dir,
            timeout=timeout,
            run_cmd=self.run,
        )

        process.check_returncode()

        log.info(
            "Finished make",
            workspace=self.number,
            work_dir=str(self.work_dir),
        )

    @session_op
    def get_libs(self, timeout=None):
        """
        Collects libraries for new_fdm.exe

        Arguments:
          timeout: Amount of time to wait before force-clising get_libs
            (Default: None)
        """

        log.info(
            "Starting get_libs",
            workspace=self.number,
            work_dir=str(self.work_dir),
        )

        process = ops.get_libs(
            exe=self.work_dir / "bin" / "new_fdm.exe",
            cwd=self.work_dir,
            log_dir=self.work_dir,
            timeout=timeout,
            run_cmd=self.run,
        )

        process.check_returncode()

        log.info(
            "Finished get_libs",
            workspace=self.number,
            work_dir=str(self.work_dir),
        )

    @session_op
    def write_srcs(self, srcs):
        """
        Will write a set of input source files into the workspace.
        """

        log.info(
            "Writing source files to work directory.",
            workspace=self.number,
            work_dir=str(self.work_dir),
            files=[str(f) for f in srcs.files],
        )

        srcs.write_dir(
            self.work_dir,
            mkdir=False,
            overwrite=True,
        )

        log.info(
            "Finished writing source files to work directory.",
            workspace=self.number,
            work_dir=str(self.work_dir),
        )

    @session_op
    def validate_build(self):
        """
        Validates that the build process was successful by making sure that key
        files exist and throwing an error otherwise.
        """

        reqs = Config[FDMCompileConfig].result_requirements
        missing = list()

        for req in reqs:
            req = Path(req)
            if not req.is_absolute():
                req = self.work_dir / req
            if not req.exists():
                missing.append(str(req))

        if len(missing) > 0:
            raise RuntimeError(
                "Build failed due to missing required output files: "
                f"{str(missing)}"
            )


    @session_op
    def build_fdm(self,
                  srcs,
                  force_autoreconf=False,
                  force_configure=False):
        """
        Runs the core operations to build the fdm exe

        Arguments:
          srcs: The bundle of src files to update
          force_autoreconf: do we run autoreconf in the woker? Implies force_configure.
          force_configure: do we run configure in the woker?
        """

        self.write_srcs(srcs)

        force_autoreconf = force_autoreconf or Config[FDMCompileConfig].force_autoreconf
        force_configure = force_configure or force_autoreconf or Config[FDMCompileConfig].force_configure

        if force_autoreconf:
            self.run_autoreconf()

        if force_configure:
            self.run_configure()

        self.run_make()

        self.get_libs()

        self.validate_build()


    @session_op
    def use_cached_build(self,
                         cached_zip : Union[str,Path]):
        """
        A stub operation that will just unpack a cached build so that
        appropriate metadata can be added.

        Useful when you need a session to produce a result archive without
        actually running the full operation.

        This just sets an internal variable storing the zip to use, all the
        actual work is done in the "generate_result_archive" function.
        As such it's idempotent and only the final call will be used.

        Arguments:
          cached_zip: The zipfile produced from the original input.
        """
        self.cached_zip = Path(cached_zip)

    @session_op
    def generate_result_archive_files(self):
        """
        Will generate a mapping between available files in a workdirectory
        and their final locations in the result archive.
        """

        log.info(
            "Generating file list for FDM compile operation.",
            workspace=self.number,
            work_dir=str(self.work_dir),
        )

        # Get the list of changed files for use w/ result_changed config option
        changed_file_map = super(FDMCompileSession,self).generate_result_archive_files()
        changed_files = list(changed_file_map.keys())

        # Add any files that are to be included on change
        result_map = apply_glob_mapping(
            Config[FDMCompileConfig].result_changed,
            files=changed_files,
        )

        # And the files that are to be included whenever they exist.
        result_map |= apply_glob_mapping(
            Config[FDMCompileConfig].result_always,
            cwd=self.work_dir,
        )

        return result_map

    @session_op
    def generate_cached_zip_archive(self):
        """
        Builds an archive at self.result_archive using the saved cached zip
        and metadata.json instead of the current state of the workspace.
        """

        if not self.cached_zip:
            raise RuntimeError(
                "Don't use generate_cached_zip_archive unless a cached zip "
                "has been provided."
            )

        log.info(
            "Using cached zip in order to create session zip.",
            cached_zip = str(self.cached_zip),
            result_archive= str(self.result_archive),
        )

        with ZipFile(self.cached_zip, 'r') as c_zip, \
             ZipFile(self.result_archive, 'w') as r_zip:

            for c_file in c_zip.namelist():

                r_file = c_file

                if c_file == 'metadata.json':
                    r_file = 'original_metadata.json'

                r_zip.writestr(
                    r_file,
                    data=c_zip.read(c_file)
                )

            cur_meta = Path(self.work_dir / self.metadata_file).resolve()

            r_zip.writestr('metadata.json', cur_meta.read_text())

    @session_op
    def generate_result_archive(self):
        """
        Uses the superclass implementation to generate the result archive and
        then adds it to the cache and copies the resulting files to various
        places.
        """

        if self.cached_zip:
            self.generate_cached_zip_archive()
        else:
            super(FDMCompileSession,self).generate_result_archive()

        for zip_loc in self.copy_zips:

            zip_loc = Path(zip_loc)
            if not zip_loc.is_absolute():
                raise RuntimeError(
                    f"Provided location for copy of result archive must be "
                    f"an absolute path instead of `{str(zip_loc)}`."
                )
            zip_loc = zip_loc.resolve()

            zip_loc.unlink(missing_ok=True)

            log.info(
                "Copying FDM Build result archive to extra location.",
                workspace=self.number,
                work_dir=str(self.work_dir),
                result_archive=str(self.result_archive),
                output=str(zip_loc),
            )

            shutil.copy2(self.result_archive, zip_loc)

        with ZipFile(self.result_archive,'r') as result_zip:

            for bin_dir in self.copy_bins:

                bin_dir = Path(bin_dir)
                if not bin_dir.is_absolute():
                    raise RuntimeError(
                        f"Provided location for extraction of result archive "
                        f"must be "
                        f"an absolute path instead of `{str(bin_dir)}`."
                    )
                bin_dir = bin_dir.resolve()

                log.info(
                    "Extracting FDM Build results to extra location.",
                    workspace=self.number,
                    work_dir=str(self.work_dir),
                    result_archive=str(self.result_archive),
                    output=str(bin_dir),
                )

                for zip_file in result_zip.namelist():
                    out_file = (bin_dir / zip_file).resolve()

                    if out_file.exists():
                        log.info(
                            "Deleting existing file from FS while extracting "
                            "fdm build results.",
                            workspace=self.number,
                            work_dir=str(self.work_dir),
                            result_archive=str(self.result_archive),
                            output=str(bin_dir),
                            zip_file = str(zip_file),
                            out_file = str(out_file),
                        )

                        out_file.unlink()

                result_zip.extractall(bin_dir)

        log.info(
            "Finished extra actions involving FDM Build results.",
            workspace=self.number,
            work_dir=str(self.work_dir),
        )
