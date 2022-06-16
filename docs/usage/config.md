# SimpleUAM Configuration System

SimpleUAM uses an internal configuration system based on
[OmegaConf](omegaconf.readthedocs.io/).
It reads YAML files in a platform specific directory for settings that are
used throughout the system.
In addition there is a utility, `suam-config`, provided with this repo to help
manage configuration information.

!!! Info "All commands are run in `<repo-root>`."

## Configuration Files

- All SimpleUAM configuration files are in [YAML](https://yaml.org/).
- We support OmegaConf's [variable interpolation](https://omegaconf.readthedocs.io/en/2.1_branch/usage.html#variable-interpolation)
  to allow referencing values in one config file from another.

## Configuration Semantics

- There is a single opinionated config directory where config files
  should be located.
- All config files overload keys from a default configuration, so you can leave
  keys (or the entire file) out if you don't want to specify them.
- Default configs are defined as attrs dataclasses in `simple_uam.util.config`
  submodules.
- Interpolation Keys for each config file are specified at init, and can be used
  to retrieve values.

## Using `suam-config`

- `pdm run suam-config dir` : Print config directory
- `pdm run suam-config list-files` : Lists valid config files in dir
- `pdm run suam-config list-keys` : Lists valid interpolation keys for configs.
- `pdm run suam-config print` : Will print current configuration to stdout
    - Options for printing all files and resolving all interpolations.
- `pdm run suam-config write` : Can write configs out to file.
    - Will default to placing fully commented out configs in the default
      configuration directory.
      User can uncomment and edit as needed.

## Existing Configuration Files

- `paths.conf.yaml` : Defaults paths for cache, logs, data, etc..
    - Used by other config defaults a lot.
    - Most people shouldn't make any changes.
    - Changes basically require reinstallation, since locations of files and
      applications will be different.
- `win_setup.conf.yaml` : Lists packages needed for windows installs of various
  components.
    - Exists to make custom automation easier.
    - Most people shouldn't make any changes.
- `craidl.conf.yaml` : Settings for working with a corpus DB or static corpus.
    - `stub_server` section controls the local stub server, defaults should be
      fine if you're only using it to generate a static corpus.
    - Other fields control whether a corpus DB or local static corpus is used
      for generating direct2cad input files. The defaults should be fine when
      using a static corpus.
- `d2c_workspace.conf.yaml` : Controls how the local processing of analysis
  jobs is done.
    - Most important field is `results_dir` which controls where the analysis
      results are placed when completed. **Most people will need to make this
      point to their shared directory.**
- `broker.conf.yaml` : Controls connections to the message broker.
    - Root properties tell where to connect to the broker.  **Most people will
      need to edit these.**
    - The `backend` section tells both the worker and client how
      to connect to the backend.
- `d2c_worker.conf.yaml` : Controls how the worker nodes run.
    - The `service` section determines how the worker node will run as a service.
        - The `auto_start` subfield controls whether the service is configured
          resume on reboot.
