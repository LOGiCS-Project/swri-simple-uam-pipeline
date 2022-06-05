from pathlib import Path

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, WinSetupConfig
from simple_uam.util.logging import get_logger

from . import choco
from .helpers import GUIInstaller, append_to_file, get_mac_address

import subprocess

log = get_logger(__name__)

graph_dep_pkg_list = [
    *Config[WinSetupConfig].global_dep_packages,
    *Config[WinSetupConfig].graph_dep_packages,
]

@task(pre=[call(choco.install, pkg=graph_dep_pkg_list)])
def dep_pkgs(ctx):
    """ Install/Update Graph Server Dependencies (idempotent) """

    log.info("Finished Installing Dependency Packages")

# Load the schema into the graphdb (gremlin)
# `:load C:\NewDeploy\docker\configDB.groovy`
# https://git.isis.vanderbilt.edu/SwRI/athens-docker-images/-/blob/master/configDB.groovy
# conf/remote.yaml: https://git.isis.vanderbilt.edu/SwRI/janusgraph/-/blob/athens/conf/remote.yaml

# Drop Entries
# `g.V().drop().iterate()`
# `g.V().count()` returns `==>0`

# Load Entries
# `g.io('/opt/janusgraph/corpus/all_schema_uam.graphml').with(IO.reader, IO.graphml).read().iterate()`
# https://git.isis.vanderbilt.edu/SwRI/athens-uav-workflows/-/tree/master/ExportedGraphML

# Get available designs:
# `g.V().hasLabel('[avm]Design').values('[]Name').unfold()`

# Check Success:
# `g.V().count()` returns `==>288604`
