from attrs import define, field
from omegaconf import SI
from .manager import Config
from .path_config import PathConfig
from .workspace_config import ResultsConfig, WorkspaceConfig
from .service_config import ServiceConfig
from typing import Optional, List

@define
class TrinityRepoConfig():
    """
    Config properties for the trinity craidl repo.
    """

    repo: str = "https://git.isis.vanderbilt.edu/SwRI/ta1/sri-ta1/trinity-craidl.git"
    """ Repo to clone """

    branch: str = "main"
    """ Branch to checkout, can be refspec. """

    examples_dir: str = "examples"
    """ Dir Containing Dirs, each w/ a 'design_swri.json' file """

@define
class GraphMLCorpusRepoConfig():
    """
    Config properties for the repo with the graphml corpus.
    """

    repo: str = "https://git.isis.vanderbilt.edu/SwRI/uam-uav-models.git"
    """ Repo to clone """

    branch: str = "12edd2bb"
    """ Branch to checkout, can be refspec. """

    graphml_file: str = 'ExportedGraphML/all_schema.graphml'
    """ Location of corpus w/in repo """

@define
class CreopysonRepoConfig():
    """
    Config properties for the creopyson package repo.
    """

    repo: str = "https://git.isis.vanderbilt.edu/SwRI/creoson/creopyson.git"
    """ Repo to clone """

    branch: str = "b9c674cd"
    """ Branch to checkout, can be refspec. """

@define
class CreosonServerConfig():
    """
    Config properties for the creoson server used by direct2Cad.
    """

    api : str = "https://git.isis.vanderbilt.edu/api/v4/projects/499/jobs/3827/artifacts/out/CreosonServerWithSetup-2.8.0-win64.zip"
    """ The API endpoint to use for downloading the prebuilt creoson server."""

    manual : str = "https://git.isis.vanderbilt.edu/SwRI/creoson/creoson-server/-/jobs/artifacts/main/raw/out/CreosonServerWithSetup-2.8.0-win64.zip?job=build-job"
    """ The manual endpoint to use for downloading creoson server. """

@define
class Direct2CadRepoConfig():
    """
    Config properties for the direct2cad repo.
    """

    repo: str = "https://git.isis.vanderbilt.edu/SwRI/uam_direct2cad.git"
    """ Repo to clone """

    branch: str = "1625709a"
    """ Branch to checkout, can be refspec. """

    exe_subdir : str = "FlightDynamics/"
    """
    Location within the above repo the alternate new_fdm.exe and associated
    dlls should go.
    """

    fdm_results_subdirs : List[str] = [
        "Results/*/fdmTB/"
    ]
    """
    List of directory globs where buildcad might put fdm outputs.
    This is where the server will look for misc FDM output files to convert
    to reasonable formats.
    """

@define
class UAVWorkflowsRepoConfig():
    """
    Config properties for the uav_workflows repo.
    """

    repo: str = "https://git.isis.vanderbilt.edu/SwRI/athens-uav-workflows.git"
    """ Repo to clone """

    branch: str = "b98d4c28"
    """ Branch to checkout, can be refspec. """

@define
class FDMCompileRepoConfig():
    """
    Config properties for SWRi's flight dynamics model repo.
    """

    repo: str = "https://git.isis.vanderbilt.edu/SwRI/flight-dynamics-model.git"
    """ Repo to clone """

    branch: str = "9e3a1ce9"
    """ Branch to checkout, can be refspec. """

@define
class FDMEvalRepoConfig():
    """
    Config properties for the environment in which SWRi's FDM repo can run.

    Both the direct2cad and UAV workflows repos should be able to act as the
    FDM environment.
    """

    repo: str = Direct2CadRepoConfig().repo
    """ Repo to clone """

    branch: str = Direct2CadRepoConfig().branch
    """ Branch to checkout, can be refspec. """

    exe_subdir : str = "FlightDynamics/"
    """
    Location within the above repo the alternate new_fdm.exe and associated
    dlls should go.
    """

    eval_subdir : str = "Results/fdmEvalResult/fdm%INDEX%/"
    """
    The directory in which input files should be placed and where the output
    files for FDM will go. Will be created if need be.

    The '%INDEX%' will be replaced by the number of the particular input
    you're evaluating.
    """




@define
class CorpusConfig():
    """
    Config properties for corpus repo repositories and files.
    This generally controls the versions of each repo/installer in use for a
    particular simple_uam deployment.

    This is separated out because it allows a deployment admin to cleanly
    control the versions of all the core repositories, incl. replacing them
    with local forks.
    """

    trinity : TrinityRepoConfig = TrinityRepoConfig()
    """
    Trinity-Craidl repo settings: used for examples.
    """

    graphml_corpus : GraphMLCorpusRepoConfig = GraphMLCorpusRepoConfig()
    """
    UAM workflow repo settings: used for graphml corpus.
    """

    creopyson : CreopysonRepoConfig = CreopysonRepoConfig()
    """
    Creopyson repo settings: used for creopyson corpus.
    """

    creoson_server : CreosonServerConfig = CreosonServerConfig()
    """
    Creoson server settings: used for downloading pre-built creoson server pkgs.
    """

    direct2cad : Direct2CadRepoConfig = Direct2CadRepoConfig()
    """
    Direct2Cad repo settings: used to define the direct2cad repo and branch.
    """

    uav_workflows : UAVWorkflowsRepoConfig = UAVWorkflowsRepoConfig()
    """
    UAV_workflows repo settings: used to define the uav_workflows repo and branch.
    """

    fdm_compile : FDMCompileRepoConfig = FDMCompileRepoConfig()
    """
    FDM Build repo settings: used to define the flight dynamics model repo and branch.
    """

    fdm_eval: FDMEvalRepoConfig = FDMEvalRepoConfig()
    """
    FDM evaluation environment repo settings: Defined the file environment
    within which calls of FDM will run.
    """

# Add to the configuration manager
Config.register(
    CorpusConfig, # class to be registered

    conf_deps = [PathConfig],

    conf_file = "corpus.conf.yaml",

    interpolation_key = "corpus",
)
