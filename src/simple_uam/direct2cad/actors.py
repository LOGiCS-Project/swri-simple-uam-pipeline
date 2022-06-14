
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
    """

    if not metadata:
        metadata = dict()
    metadata['message_info'] = message_metadata()

    with D2CWorkspace(name="gen_info_files",metadata=metadata) as session:
        session.write_design(design)
        session.gen_info_files(design)

    return session.metadata


@actor
def process_design(design, metadata=None):
    """
    Processes a design on a worker node and saves the result into a result
    archive on the worker. Returns metadata on the worker used and archive
    created.
    """

    if not metadata:
        metadata = dict()
    metadata['message_info'] = message_metadata()

    with D2CWorkspace(name="process_design",metadata=metadata) as session:
        session.process_design(design)

    return session.metadata
