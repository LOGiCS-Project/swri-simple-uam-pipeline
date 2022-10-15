
from simple_uam.workspace.session import Session, session_op
from simple_uam.util.logging import get_logger
from simple_uam.util.config import Config, D2CWorkspaceConfig, CraidlConfig
from simple_uam.util.system import backup_file
from simple_uam.craidl.corpus import GremlinCorpus, StaticCorpus, get_corpus
from simple_uam.craidl.info_files import DesignInfoFiles
from attrs import define,field
from simple_uam.worker import actor
from time import sleep

import json
import csv
from pathlib import Path

log = get_logger(__name__)

@define
class D2CSession(Session):
    """
    A workspace session specialized to the direct2cad workflow.
    """

    @session_op
    def start_creo(self):
        """
        Runs startCreo.bat in order to ensure that creoson and an instance
        of creo is running.
        """

        log.info(
            "Starting Creo.",
            workspace=self.number,
        )

        # For some reason startCreo.bat does nothing now, so we'll just do
        # the same thing in python.

        # self.run(
        #     ["startCreo.bat"],
        #     input="y\n",
        #     text=True,
        #     )

        self.run(["python", "startCreo.py"])
        wait_time=5
        for i in range(1, wait_time):
            log.info(
                f"Waiting for Creo Start {i}s / {wait_time}s"
            )
            sleep(1)

    @session_op
    def write_design(self, design, out_file="design_swri.json"):
        """
        Writes the design data to a file in the work directory.

        Arguments:
          design: The design object itself.
          out_file: The file, within the workdir, to write to.
            Default: 'design_swri.json'
        """

        out_file = Path(out_file)

        if out_file.is_absolute():
            raise RuntimeError("out_file for writing design must be relative.")

        out_file = self.work_dir / out_file

        if out_file.exists():
            raise RuntimeError("out_file already exists.")

        log.info(
            "Writing design to output file.",
            workspace=self.number,
            out_file=str(out_file),
        )

        with out_file.open('w') as fp:
            json.dump(design, fp, indent="  ")

    @session_op
    def write_study_params(self, params, out_file="study_params.csv"):
        """
        Writes the study parameters to a file in the data directory.

        Arguments:
          params: The params as an array of dictionaries each containing a
            row of parameters.

            Note: There must be at least one item in params.
            Note: All of the dictionaries must have the same set of keys.
          out_file: The file, in the working directory, that the study params
            will be written to. By default `study_params.csv`.
        """

        out_file = Path(out_file)

        if out_file.is_absolute():
            raise RuntimeError("out_file for writing study params must be relative.")

        out_file = self.work_dir / out_file

        if len(params) == 0:
            raise RuntimeError("Study params list must have at least one element.")

        if any([a.keys() != b.keys() for a in params for b in params]):
            raise RuntimeError("Study params dictionaries do not have identical key sets.")

        param_fields = params[0].keys()
        base_fields = Config[D2CWorkspaceConfig].study_params.field_order
        # normalizes the fields to ensure that likely errors collide w/ base
        norm = lambda f: f.lower().strip().strip("_")
        normed_fields = [norm(f) for f in base_fields]
        field_order = list()

        # Get the initial ordered set of fields
        for field in base_fields:
            if field in param_fields:
                field_order.append(field)

        # Gather remaining fields
        for field in param_fields:

            # Check if cases are right, because it's an easy error to miss
            if (field not in base_fields) and (norm(field) in normed_fields):
                correct = base_fields[normed_fields.index(norm(field))]
                raise RuntimeError(
                    f"Field {repr(field)} should be {repr(correct)} in order "
                    "for SWRi's code to work correctly.")

            # Append field to order list if needed.
            if field not in field_order:
                field_order.append(field)

        # Clean up out_file if it exists
        out_file.unlink(missing_ok=True)

        # Write param info out as a CSV
        with out_file.open('w') as fp:

            log.info(
                "Writing study params to output file.",
                workspace=self.number,
                out_file=str(out_file),
                field_order=field_order,
                params=params,
            )

            writer = csv.DictWriter(fp, fieldnames=field_order)
            writer.writeheader()
            writer.writerows(params)






    @session_op
    def gen_info_files(self, design):
        """
        Creates info files in the target directory from the provided design
        data.

        Arguments:
           design: The design as returned by json.load or similar.
        """

        log.info(
            "Initializing corpus.",
            workspace=self.number,
        )

        corpus = get_corpus(
            config=Config[CraidlConfig]
        )

        log.info(
            "Generating info files.",
            workspace=self.number,
        )

        info_files = DesignInfoFiles(corpus=corpus, design=design)

        log.info(
            "Writing info files to workspace.",
            workspace=self.number,
        )

        info_files.write_files(self.work_dir)

    @session_op
    def build_cad(self):
        """
        Runs buildcad.py on the currently loaded info files,
        leaving changes and parsed results in place for session cleanup
        to manage.
        """

        self.start_creo()


        stdout_file = self.work_dir / 'buildCad.stdout'
        stderr_file = self.work_dir / 'buildCad.stderr'

        backup_file(stdout_file, self.work_dir, delete=True, missing_ok=True)
        backup_file(stderr_file, self.work_dir, delete=True, missing_ok=True)

        log.info(
            "Starting buildcad.py",
            workspace=self.number,
        )

        with stdout_file.open('w') as so, stderr_file.open('w') as se:
            self.run(
                ["python", "buildcad.py"],
                stdout=so,
                stderr=se,
            )

    @session_op
    def process_design(self, design, study_params=None):
        """
        Runs the chain of operations needed to process a single uam design
        and produce FDM, cad, and other output.
        """

        if not study_params:
            study_params = Config[D2CWorkspaceConfig].study_params.default

        self.write_design(design)
        self.write_study_params(study_params)
        self.gen_info_files(design)
        self.build_cad()
