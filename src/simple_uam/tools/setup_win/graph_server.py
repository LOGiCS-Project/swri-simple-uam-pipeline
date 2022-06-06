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

# {- Get janusgraph downloaded and extracted
# wget.exe https://github.com/JanusGraph/janusgraph/releases/download/v0.6.1/janusgraph-full-0.6.1.zip
# 7z x .\janusgraph-full-0.6.1.zip -}

# Clone docker images and uav workflows
# git clone https://git.isis.vanderbilt.edu/SwRI/athens-docker-images.git
# git clone https://git.isis.vanderbilt.edu/SwRI/athens-uav-workflows.git --branch uam_corpus

# -- Choco install hadoop -y
# you do need a version of java that installs java.exe

# Get gremlin console & unzip
# https://dlcdn.apache.org/tinkerpop/3.6.0/apache-tinkerpop-gremlin-console-3.6.0-bin.zip

# Get gremlin server and unzip (make sure version is 3.5 to match bitsy)
# https://downloads.apache.org/tinkerpop/3.5.3/apache-tinkerpop-gremlin-server-3.5.3-bin.zip

# Setup Bitsy 3.5:
# Instructions here: https://github.com/lambdazen/bitsy/wiki

# Get winutils
# cd .\bin\
# wget.exe  https://github.com/cdarlint/winutils/raw/master/hadoop-2.8.5/bin/winutils.exe

# Load the schema into the graphdb (gremlin)
# `:load C:\NewDeploy\docker\configDB.groovy`
# https://git.isis.vanderbilt.edu/SwRI/athens-docker-images/-/blob/master/configDB.groovy
# conf/remote.yaml: https://git.isis.vanderbilt.edu/SwRI/janusgraph/-/blob/athens/conf/remote.yaml

"""
Aha, here's a basic session.

gremlin> graph = TinkerGraph.open()
==>tinkergraph[vertices:0 edges:0]
gremlin> g = traversal().withEmbedded(graph)
==>graphtraversalsource[tinkergraph[vertices:0 edges:0], standard]
gremlin> g.V().drop()
gremlin> import org.apache.tinkerpop.gremlin.structure.VertexProperty.Cardinality
gremlin> g.V().drop().iterate()
gremlin> g.V().count()
==>0
gremlin> g.io('all_schema_uam.graphml').with(IO.reader, IO.graphml).read().iterate()
gremlin> g.V().count()
==>176921
gremlin> g.V().hasLabel('[avm]Design').values('[]Name').unfold()
==>NuSpade
==>Tree
==>Rake
==>Trowel
==>AllComponentsUAM
"""

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
