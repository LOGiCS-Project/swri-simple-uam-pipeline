
from simple_uam.workspace.session import Session, session_op
from simple_uam.util.logging import get_logger
from simple_uam.craidl.corpus import GremlinCorpus, StaticCorpus, get_corpus
from simple_uam.craidl.info_files import DesignInfoFiles
from simple_uam.worker import actor, message_metadata
from attrs import define,field
import json
from pathlib import Path
from simple_uam.util.invoke import task, call
from simple_uam.util.logging import get_logger
from simple_uam.direct2cad.workspace import D2CWorkspace

log = get_logger(__name__)

@actor
def gen_info_files(design, metadata=None):
    """
    gen_info_files as an actor that will perform the task on a worker node
    and return metadata information.

    Arguments:
      design: The design to generate the info files for as a JSON serializable
        python object.
      metadata: An arbitrary JSON serializable object that will be included
        in 'metadata.json' under the 'user_metadata' field.
    """

    internal_data = dict()
    if metadata:
        internal_data['user_metadata'] = metadata
    internal_data['message_info'] = message_metadata()

    with D2CWorkspace(name="gen_info_files",metadata=internal_data) as session:
        session.write_design(design)
        session.gen_info_files(design)

    return session.metadata


@actor
def process_design(design, metadata=None, study_params=None):
    """
    Processes a design on a worker node and saves the result into a result
    archive on the worker. Returns metadata on the worker used and archive
    created.

    Arguments:
      design: The design to be processed as a JSON serializable object.
      metadata: A JSON serializable metadata object that will be placed
        in 'metadata.json' under the field 'user_metadata'.
      study_params: A list of dictionaries each containing one set of study
        parameters to run analyses for. The list must have at least one entry
        and the dictionaries must all have the same keys set.
    """

    internal_data = dict()
    if metadata:
        internal_data['user_metadata'] = metadata
    internal_data['message_info'] = message_metadata()

    with D2CWorkspace(name="gen_info_files",metadata=internal_data) as session:
        session.process_design(design, study_params=study_params)

    return session.metadata
