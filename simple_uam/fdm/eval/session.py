
from simple_uam.workspace.session import Session, session_op
from simple_uam.util.logging import get_logger
from simple_uam.util.config import Config, FDMEvalConfig, CorpusConfig
from simple_uam.util.system import backup_file, configure_file
from simple_uam.util.system.glob import apply_glob_mapping
import simple_uam.util.system.backup as backup
from simple_uam.fdm.parsing import parse_path_data
from simple_uam.util.exception import contextualize_exception
from zipfile import ZipFile
import zipfile
import tempfile
from attrs import define,field
from contextlib import contextmanager
from simple_uam.worker import actor
from time import sleep
import shutil
import json
import f90nml
import traceback
from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic
import csv
from pathlib import Path

log = get_logger(__name__)

@define
class FDMEnvSession(Session):
    """
    A workspace session specialized to setting up FDM env within a
    d2c_session and parsing FDM inputs and outputs.
    """

    @property
    def exe_subdir(self):
        """
        The subdirectory where the fdm exe should be placed when evaluating new
        inputs.
        """
        return Config[CorpusConfig].fdm_eval.exe_subdir

    @property
    def exe_dir(self):
        """
        The full path to the exe directory,
        """
        return Path(self.work_dir / self.exe_subdir).resolve()

    @property
    def exe_path(self):
        """
        The path to the new_fdm.exe
        """
        return Path(self.exe_dir / 'new_fdm.exe').resolve()

    @session_op
    def extract_fdm_exe(self,
                        bin_zip):
        """
        Will extract a zipfile containing the FDM executable into the
        appropriate location.

        Arguments:
          bin_zip: must be an absolute path.
        """

        if bin_zip == None:
            log.info(
                "No binary zip provided when extracting fdm exe, skipping.",
                workspace=self.number,
                work_dir=str(self.work_dir),
            )
            return

        bin_zip = Path(bin_zip)

        if not bin_zip.is_absolute():
            raise RuntimeError(
                "Provided path to new_fdm zip must be an absolute path."
            )

        if not bin_zip.exists():
            raise RuntimeError(
                f"No executable binaries zip file found at `{str(bin_zip)}`."
            )

        self.exe_dir.mkdir(parents=True, exist_ok=True)

        with ZipFile(bin_zip, mode='r') as b_z:

            exe_path = zipfile.Path(b_z, "new_fdm.exe")

            if not exe_path.exists():
                raise RuntimeError(
                    f"Could not find executable `{str(exe_path)}` within "
                    f"archive `{str(bin_zip)}`, are you sure this zip "
                    "contains the fdm executable?"
                )

            # clear up dir if needed
            for out_file in b_z.namelist():
                out_file = Path(self.exe_dir / out_file)

                if out_file.exists():
                    log.info(
                        "File already exists when extracting binaries.",
                        workspace=self.number,
                        work_dir=str(self.work_dir),
                        file=str(out_file),
                        bin_zip=str(bin_zip),
                    )

                    out_file.unlink()

        log.info(
            "Extracting executable binaries to appropriate dir",
            workspace=self.number,
            work_dir=str(self.work_dir),
            bin_zip=str(bin_zip),
            exe_dir=str(self.exe_dir),
        )

        with ZipFile(bin_zip, mode='r') as b_z:
            self.exe_dir.mkdir(parents=True, exist_ok=True)
            b_z.extractall(path=self.exe_dir)

    @session_op
    def write_raw(self,
                  file_path,
                  data):
        """
        Writes the data provided to file_path.

        Arguments:
          file_path: The file, relative to the work_dir, to write to.
          data: The raw string data to write.
        """

        file_loc = self.to_workpath(file_path)

        file_loc.parent.mkdir(parents=True, exist_ok=True)

        log.info(
            f"Writing raw data to output file.",
            workspace=self.number,
            work_dir=str(self.work_dir),
            output_file=str(file_loc),
        )

        if isinstance(data, str):
            file_loc.write_text(data)
        elif isinstance(data, bytes):
            file_loc.write_bytes(data)
        else:
            raise RuntimeError(
                f"Input data must be of type str or bytes. "
                f"Instead found {type(data).__name__}."
            )

    @session_op
    def write_json(self,
                   file_path,
                   data):
        """
        Writes the data provided to the file_path in JSON format.

        Arguments:
          file_path: The file, relative to the work_dir, to write to.
          data: The raw string data to write.
        """

        file_loc = self.to_workpath(file_path)

        file_loc.parent.mkdir(parents=True, exist_ok=True)

        log.info(
            f"Writing JSON data to output file.",
            workspace=self.number,
            work_dir=str(self.work_dir),
            output_file=str(file_loc),
        )

        with file_loc.open('w') as fp:
            json.dump(data, fp, indent=2, sort_keys=True)

    @session_op
    def write_namelist(self,
                       file_path,
                       data):
        """
        Writes the data provided to the file_path in namelist format.

        Arguments:
          file_path: The file, relative to the work_dir, to write to.
          data: The raw string data to write.
        """

        file_loc = self.to_workpath(file_path)

        file_loc.parent.mkdir(parents=True, exist_ok=True)

        log.info(
            f"Writing namelist data to output file.",
            workspace=self.number,
            work_dir=str(self.work_dir),
            output_file=str(file_loc),
        )

        with file_loc.open('w') as fp:
            f90nml.write(data,fp)

    @session_op
    def write_csv(self,
                  file_path,
                  data,
                  fieldnames,
                  **kwargs):
        """
        Writes the data provided to the file_path in csv format.

        Arguments:
          file_path: The file, relative to the work_dir, to write to.
          data: The raw string data to write.
          fieldnames: fieldnames to write entries under.
          **kwargs: extra args to pass to csv.DictWriter
        """

        file_loc = self.to_workpath(file_path)

        file_loc.parent.mkdir(parents=True, exist_ok=True)

        log.info(
            f"Writing csv data to output file.",
            workspace=self.number,
            work_dir=str(self.work_dir),
            output_file=str(file_loc),
            fieldnames=[str(f) for f in fieldnames],
            **kwargs,
        )

        with file_loc.open('w') as fp:

            writer = csv.DictWriter(fp, fieldnames, **kwargs)
            writer.writeheader()
            writer.writerows(data)

    @session_op
    def read_raw(self,
                 file_path,
                 text=True):
        """
        Reads a raw file from the file_path and returns the contents.

        Arguments:
          file_path: The file, relative to the work_dir, to read from.
          text: if true read str else bytes
        """

        file_loc = self.to_workpath(file_path)

        log.info(
            f"Reading raw data from input file.",
            workspace=self.number,
            work_dir=str(self.work_dir),
            input_file=str(file_loc),
        )

        if text:
            return file_loc.read_text()
        else:
            return file_loc.read_bytes()

    @session_op
    def read_path_data(self,
                       file_path):
        """
        Reads a path_data file from file_path and returns the contents.

        Arguments:
          filename: The file, within eval_dir, to read from.
          index: The index of the eval dir to write to.
          text: if true read str else bytes

        Returns:
          data: A list of dicts for each data entry
          fieldnames: An ordered list of fieldnames to use.
        """

        path_data = self.read_raw(file_path, text=True)

        return parse_path_data(path_data)

    @session_op
    def read_json(self,
                  file_path):
        """
        Reads a JSON file from the file_path and returns the contents.

        Arguments:
          file_path: The file, relative to the work_dir, to read from.
        """

        file_loc = self.to_workpath(file_path)

        log.info(
            f"Reading JSON data from input file.",
            workspace=self.number,
            work_dir=str(self.work_dir),
            input_file=str(file_loc),
        )

        with file_loc.open('r') as fp:
            return json.load(fp)

    @session_op
    def read_namelist(self,
                      file_path):
        """
        Reads a fortran namelist file from the file_path and returns the
        contents.

        Arguments:
          file_path: The file, relative to the work_dir, to read from.
        """

        file_loc = self.to_workpath(file_path)

        log.info(
            f"Reading fortran namelist from input file.",
            workspace=self.number,
            work_dir=str(self.work_dir),
            input_file=str(file_loc),
        )

        with file_loc.open('r', errors='backslashreplace') as fp:
            return f90nml.read(fp)

    @session_op
    @contextmanager
    def write_exception(self,
                        file_path,
                        context = None,
                        supress = False):
        """
        A context manager that will catch any exceptions within it and write
        it to file.

        Arguments:
          file_path: The file to write the exception to.
          context: The context used in log messages for the exception.
            (Default: none)
          supress: Will supress any thrown exceptions if true, otherwise
            reraise them for callers to handle. (Default: False)
        """

        try:
            yield
        except Exception as exc:

            exc_data = contextualize_exception(exc, show_locals=True)

            log.error(
                "Catching exception and adding to log.",
                workspace=self.number,
                work_dir=str(self.work_dir),
                error_file=str(file_path),
                context=context,
            )

            self.log_exception(exc)

            err_lines = [
                f"Caught error when performing operation.\n",
                f"  context: {context}\n",
                f"\n",
                f"More detailed error data can be found in metadata.json.\n",
                f"\n",
            ]
            err_lines += traceback.format_exception(err)

            self.write_raw(
                file_path,
                ''.join(err_lines),
            )

            if not supress:
                raise exc

    @session_op
    def nml_to_json(self,
                    input_path,
                    output_path = None,
                    error_path = None):
        """
        Converts a namelist to a json file.

        Arguments:
          input_path
        """

        if not output_path:
            output_path = str(input_path) + ".json"

        if not error_path:
            error_path = str(output_path) + ".error"

        input_loc  = self.to_workpath(input_path)
        output_loc = self.to_workpath(output_path)
        error_loc  = self.to_workpath(error_path)

        output_loc.parent.mkdir(parents=True, exist_ok=True)
        error_loc.parent.mkdir(parents=True, exist_ok=True)

        with self.write_exception(
                error_loc,
                context="Failed to convert namelist to JSON",
                supress=True,
        ):
            data = self.read_namelist(input_loc)
            self.write_json(output_loc,data)

    @session_op
    def path_to_csv(self,
                    input_pth,
                    output_path = None,
                    error_path = None):
        """
        Converts a path file to a json file.
        """

        if not output_path:
            output_path = str(input_path) + ".csv"

        if not error_path:
            error_path = str(output_path) + ".error"

        input_loc  = self.to_workpath(input_path)
        output_loc = self.to_workpath(output_path)
        error_loc  = self.to_workpath(error_path)

        output_loc.parent.mkdir(parents=True, exist_ok=True)
        error_loc.parent.mkdir(parents=True, exist_ok=True)

        with self.write_exception(
                error_loc,
                context="Failed to convert path data to csv file.",
                supress=True,
        ):
            (data, fieldnames) = self.read_path_data(input_loc)
            self.write_csv(output_loc,data,fieldnames)

    @session_op
    def all_nml_to_json(self,
                        eval_dir: Union[str,Path]):
        """
        Converts all configured nml files to their json equivalent.

        Arguments:
          eval_dir: The directory in which to look for nml files.
        """

        eval_dir = self.to_workpath(eval_dir)
        eval_dir.mkdir(parents=True, exist_ok=True)

        globs = Config[FDMEvalConfig].nml_to_json
        files = [f for g in globs for f in eval_dir.glob(g)]

        for nml_file in files:
            log.info(
                "Converting nml to json",
                workspace=self.number,
                work_dir=str(self.work_dir),
                nml_file = str(nml_file),
                eval_dir = str(eval_dir),
            )
            self.nml_to_json(nml_file)

    @session_op
    def all_path_to_csv(self,
                        eval_dir: Union[str,Path]):
        """
        Converts all configured nml files to their json equivalent.

        Arguments:
          eval_dir: The directory in which to look for nml files.
        """

        eval_dir = self.to_workpath(eval_dir)
        eval_dir.mkdir(parents=True, exist_ok=True)

        globs = Config[FDMEvalConfig].path_to_csv
        files = [f for g in globs for f in eval_dir.glob(g)]

        for path_file in files:
            log.info(
                "Converting pathfile to csv",
                workspace=self.number,
                work_dir=str(self.work_dir),
                path_file = str(nml_file),
                eval_dir = str(eval_dir),
            )
            self.path_to_csv(path_file)

@define
class FDMEvalSession(FDMEnvSession):
    """
    A workspace session specialized to evaluating the FDM within a direct2cad
    repository.
    """

    indices : List[str] = field(
        factory = list,
        init = False,
    )
    """
    Internal list of all evaluated inputs by index.
    """

    def eval_subdir(self, index):
        """
        The subdirectory within each workspace where we place input files,
        find output files, and evaluate FDM.
        """

        base = Config[CorpusConfig].fdm_eval.eval_subdir
        flag = '%INDEX%'

        if base.count(flag) != 1:
            raise RuntimeError(
                f"The provided eval subdir {repr(base)} should contain exactly "
                f"one instance of the flag {repr(flag)}."
            )

        index = str(index)

        if index != Path(index).stem or '.' in index:
            raise RuntimeError(
                f"Sample index cannout contain directory markers or file "
                f"extensions. {repr(index)} is invalid because it could "
                "be mistaken for a directory path or file."
            )

        return base.replace(flag,index)

    def eval_dir(self, index):
        """
        The eval dir for a particular input index.
        """
        return Path(self.work_dir / self.eval_subdir(index)).resolve()

    @session_op
    def run_fdm(self,
                input_file,
                index,
                stdout='new_fdm.stdout',
                stderr='new_fdm.stderr',
                timeout=None,
    ):
        """
        Runs new_fdm.exe in the given eval directory using the given input file
        and producing the stdout and stderr files.

        Arguments:
          input_file: The input to be piped into new_fdm.exe.
          index: The index of the operation.
          stdout: the name of the stdout dump.
          stderr: the name of the stderr dump.
          timeout: How long to wait for the operation to complete.
        """

        eval_dir = self.eval_dir(index)
        eval_dir.mkdir(parents=True, exist_ok=True)
        stdout = self.to_workpath(stdout, eval_dir)
        stderr = self.to_workpath(stderr, eval_dir)
        input_file = self.to_workpath(input_file, eval_dir)

        log.info(
            "Running new_fdm.exe for input.",
            workspace=self.number,
            work_dir=str(self.work_dir),
            exe_path=str(self.exe_path),
            cwd=str(eval_dir),
            stdin=str(input_file),
            stdout=str(stdout),
            stderr=str(stderr),
            timeout=timeout,
        )

        with stdout.open('w') as so, \
             stderr.open('w') as se, \
             input_file.open('r') as si:

            process = self.run(
                [self.exe_path],
                cwd=eval_dir,
                stdin=si,
                stdout=so,
                stderr=se,
                timeout=timeout,
                text=True,
            )

    @session_op
    def eval_fdm(self,
                 data,
                 index):
        """
        Evaluates the specific input data in the eval dir specified by the
        provided index, does additional processing of outputs.

        Arguments:
          data: the json object to be used as an input to the document.
          index: the specific eval directory to use.
        """

        index = str(index)

        # Keep track of inputs you've seen for results management
        if index in self.indices:
            raise RuntimeError(
                f"Cannot write to same index `{str(index)}` twice in a single "
                "session.")
        self.indices.append(index)

        # Rename things for convenience
        eval_dir = self.eval_dir(index)
        input_nml = self.to_workpath('flightDynFast.inp',eval_dir)
        output_swri = self.to_workpath('flightDynFastOut.out',eval_dir)

        # Write out input data
        self.write_namelist(input_nml,data)

        # Actually run the fdm exe
        self.run_fdm(
            input_nml,
            index,
            stdout=output_swri,
        )

        # Some post processing of output.
        self.all_nml_to_json(eval_dir)
        self.all_path_to_csv(eval_dir)

    @session_op
    def eval_fdms(self, data_map):
        """
        Evaluates all the data inputs in the data_map.

        Arguments:
          data_map: Map from input data index to input data.
        """

        for index, data in data_map.items():
            self.eval_fdm(data, index)

    @session_op
    def generate_result_archive_files(self):
        """
        Will generate a mapping between available files in a workdirectory
        and their final locations in the result archive.
        """

        log.info(
            "Generating file list for FDM eval operation.",
            workspace=self.number,
            work_dir=str(self.work_dir),
        )

        # Get the list of changed files for use w/ result_changed config option
        changed_file_map = super(FDMEvalSession,self).generate_result_archive_files()
        changed_files = list(changed_file_map.keys())

        # Add any files that are to be included on change
        result_map = apply_glob_mapping(
            Config[FDMEvalConfig].result_changed,
            files=changed_files,
        )

        # And the files that are to be included whenever they exist.
        result_map |= apply_glob_mapping(
            Config[FDMEvalConfig].result_always,
            cwd=self.work_dir,
        )

        # Gather all the evaluated data
        for index in self.indices:

            eval_dir = self.eval_dir(index)
            target_dir = Path("run-" + str(index))
            data_files = eval_dir.rglob("*")

            for f in data_files:

                f = f.relative_to(eval_dir)
                source = str(eval_dir / f)
                target = str(target_dir / f)
                result_map[source] = target

        return result_map
