
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
        wait_time=20
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
    def process_design(self, design):
        """
        Runs the chain of operations needed to process a single uam design
        and produce FDM, cad, and other output.
        """

        self.write_design(design)
        self.gen_info_files(design)
        self.build_cad()
