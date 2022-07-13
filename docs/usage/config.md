# SimpleUAM Configuration System

SimpleUAM uses an internal configuration system based on
[OmegaConf](omegaconf.readthedocs.io/).
It reads YAML files in a platform specific directory for settings that are
used throughout the system.
In addition there is a utility, `suam-config`, provided with this repo to help
manage configuration information.

!!! Info "All commands are run in `<repo-root>`."

## Configuration Semantics {#semantics}

The SimpleUAM configuration model is based on a few core principles:

- Configuration variables are split into two categories:
    - Per-machine: These are unique to a single
      machine, but are shared between all the processes or tasks on that machine.
    - Per-deployment: These are unique to single deployment are can be shared
      without modification between all the machines in a deployment.
- Configuration files are split into per-machine and per-deployment categories
  as well so that they can respectively be defined locally and linked from a
  central shared location.
- At a per-machine level there is a single opinionated config directory where
  all config files must be found.
- Config files come with functional defaults whenever possible.
- Config files can be defined partially, with missing fields being populated
  by defaults or lower priority config files.

Together these guidelines give us a basic model of configuration semantics
based on a fixed root location for files, incremental overloading, and
linking of shared configuration into the fixed root.

### Root Directory {#semantics-root}

Config files are all located in an fixed root directory.
Run the following to find that directory:

```bash
pdm run suam-config dir
```

See [this section](#cli-dir) for more information on the command and
[here](#files) for information on the specific config files you can find there.

### Overloading {#semantics-overloading}

You can incrementally define configurations with multiple files that overload
each other.

There are 3 general levels of configuration options, from lowest to highest
priority.

- **Default**: These are defined in the code as a python class.
  Attributes in that class correspond to fields of the config file.
- **Base Config**: This is the base configuration directory as
  found with `pdm run suam-config dir`.
- **CLI Argument Config**: This is the config dir added to the stack when
  a command is given `--config-dir=<config-dir-arg>` as an argument.

For example consider the case for a hypothetical `foo.conf.yaml` and the
raw definitions of each configuration:

=== "Default"

    ``` python linenums="1" title="util/config/foo_config.py"
    from attrs import define

    @define
    class FooConfig():

        name : str = "John"
        age  : int = 23
        occupation : str = "Example Salesman"
        hobby : str = "Sampling"
    ```

=== "Base Config"

    ``` yaml linenums="1" title="config-dir/foo.conf.yaml"
    name: Andy
    hobby: Cooking
    ```

=== "CLI Argument Config"

    ``` yaml linenums="1" title="config-dir-arg/foo.conf.yaml"
    name: Jane
    age: 32
    ```

And the corresponding config as seen by the program in each case.

=== "Default"

    These are configuration values when:

    - No `config-dir/foo.conf.yaml` exists
    - No `--config-dir=config-dir-arg` argument has been used

    ``` yaml linenums="1" title="Loaded, In-Memory Configuration"
    name: John
    age: 23
    occupation: Example Salesman
    hobby: Sampling
    ```

=== "Base Config"

    These are the loaded values when:

    - `config-dir/foo.conf.yaml` exists
    - `--config-dir=config-dir-arg` isn't an argument

    ``` yaml linenums="1" hl_lines="1 4" title="Loaded, In-Memory Configuration"
    name: Andy
    age: 23
    occupation: Example Salesman
    hobby: Cooking
    ```
    Note how only the values in `<config-dir>/foo.conf.yaml` change with the
    rest remaining at their defaults.

=== "CLI Argument Config"

    These are the loaded values when

    - `config-dir/foo.conf.yaml` exists
    - `config-dir-arg/foo.conf.yaml` exists
    - A `--config-dir=config-dir-arg` argument was given

    ``` yaml linenums="1" hl_lines="1 2" title="Loaded, In-Memory Configuration"
    name: Jane
    age: 32
    occupation: Example Salesman
    hobby: Cooking
    ```

Look [here](#files) for information on the specific config files, their source
locations, expected filenames, and key fields.

### Linking {#semantics-linking}

The ideal way to work with per-deployment configs is to put them all in a
single location, accessible from all the nodes in your deployment, and
symlink them into the root configuration directories of each machine.

See [the `install` command](#cli-install), which makes that process easier.
Also see the [individual config files](#files) for information on whether each
file is per-machine or per-deployment.

## Configuration File Format {#format}

All SimpleUAM configuration files are in [YAML](https://yaml.org/).
See [this guide](https://circleci.com/blog/what-is-yaml-a-beginner-s-guide/)
for a quick introduction to the format.

### Variable Interpolation {#format-inter}

We support OmegaConf's [variable interpolation](https://omegaconf.readthedocs.io/en/2.1_branch/usage.html#variable-interpolation)
to allow referencing values in one config file from another.

Terms between `${` and `}` in a configuration variable are interpreted as a
reference to another field in the current configuration or, with the appropriate
key, a field in another configuration file.

!!! tip ""
    Interpolation happens after *all* config files are loaded and all
    overloading is finished.

#### Basic Interpolation {#format-inter-basic}

Within a single file you can interpolate variables at the same level:

```yaml linenums="1" title="Raw Config" hl_lines="2 4 7"
field1: Test
field2: Field1 is '${field1}'
field3: 123
field4: ${field3}
subsection:
  field1: Other Value
  field2: Sibling Field1 is '${field1}'
```

Which resolves to:

```yaml linenums="1" title="Resolved Config" hl_lines="2 4 7"
field1: Test
field2: Field1 is 'Test'
field3: 123
field4: 123
subsection:
  field1: Other Value
  field2: Sibling Field1 is 'Other Value'
```

#### Advanced Interpolation {#format-inter-advanced}

You can also look at parent and child fields with interpolation:

```yaml linenums="1" title="Raw Config" hl_lines="2 5"
field1: Test
field2: Child Field1 is '${subsection.field1}'
subsection:
  field1: Other Value
  field2: Parent Field1 is '${.field1}'
```

Which resolves to:

```yaml linenums="1" title="Resolved Config" hl_lines="2 5"
field1: Test
field2: Child Field1 is 'Other Value'
subsection:
  field1: Other Value
  field2: Parent Field1 is 'Test'
```

#### Cross-File Interpolation {#format-inter-cross-file}

Each SimpleUAM config file also comes with an interpolation key, which can be
used to reference its fields in other locations.

Consider the following config with the interpolation key `"example"`:

```yaml linenums="1" title="Config w/ Key 'example'"
parent-field: Example Parent
subsection:
  sub-field: Example Child
```

And the following raw config:

```yaml linenums="1" title="Raw Config"
field1: Parent is '${example:parent-field}'
field2: Child is '${example:subsection.sub-field}'
```

Which resolves to:

```yaml linenums="1" title="Resolved Config"
field1: Parent is 'Example Parent'
field2: Child is 'Example Child'
```

See [each config file's info](#field) to find out their interpolation keys.

## Using the `suam-config` CLI {#cli}

There is an `suam-config` script included with SimpleUAM for manipulating
configuration files.

You can get a list of all of its sub-commands by running:

```bash
pdm run suam-config --list
```

Each sub-command has help output that can be accessed with:

```bash
pdm run suam-config <sub-command> --help
```

More details on each sub-command follow.

### The `dir` sub-command {#cli-dir}

The `dir` command prints out the current, highest-priority config directory.
It can be run as follows:

```bash
pdm run suam-config dir
```

**Arguments**:

- **`--all`/`-a`**: This prints out a list of all the config directories that
  are being read from lowest to highest priority.
  Only useful when called with `--config-dir=`.

### The `list-*` sub-commands {#cli-list}

The various `list-*` commands print out information on each of the configuration
files.
The outputs can be used to specify individual config files for the `file`,
`print`, `write`, and `install` commands.

#### `list-files` {#cli-list-files}

Prints a list of recognized configuration files that are searched for in each
configuration directory.
It can be run as follows:

```bash
pdm run suam-config list-files
```

??? example "Sample Output of `pdm run suam-config list-files`"

    ```bash
    paths.conf.yaml
    auth.conf.yaml
    win_setup.conf.yaml
    craidl.conf.yaml
    corpus.conf.yaml
    d2c_workspace.conf.yaml
    broker.conf.yaml
    d2c_worker.conf.yaml
    ```

Each output filename can be used as a config file identifier in other commands.

#### `list-keys` {#cli-list-keys}

Prints a list of recognized interpolation keys.
It can be run as follows:

```bash
pdm run suam-config list-keys
```

??? example "Sample Output of `pdm run suam-config list-keys`"

    ```bash
    path
    auth
    win_setup
    craidl
    corpus
    d2c_workspace
    broker
    d2c_worker
    ```

Each interpolation key can be used in configuration files and as a config file
identifier in other commands.

#### `list-classes` {#cli-list-classes}

Prints a list of python classes corresponding to each configuration file.
It can be run as follows:

```bash
pdm run suam-config list-classes
```

??? example "Sample Output of `pdm run suam-config list-classes`"

    ```bash
    PathConfig
    AuthConfig
    WinSetupConfig
    CraidlConfig
    CorpusConfig
    D2CWorkspaceConfig
    BrokerConfig
    D2CWorkerConfig
    ```

Each python class name can be used as a config file identifier in other commands.

### The `file` sub-command {#cli-file}

The `file` sub-command is the single-file counterpart to the `dir` sub-command.
It prints out where SimpleUAM is looking for a configuration file.
It can be run as follows:

```bash
pdm run suam-config file -c <config-id>
```

**Arguments**:

- **`--config=STRING`/`-c STRING`** (Mandatory) : The config file whose search
  location you're asking for.
  "`STRING`" can be any of the output lines from the `list-*` subcommands.
- **`--all`/`-a`**: This prints out a list of all the config file that
  are being read from lowest to highest priority.
  Only useful when called with `--config-dir=`.

### The `print` sub-command {#cli-print}

The `print` sub-command will print out the currently loaded configuration
after all input files have been read and processed.
This is the configuration as other parts of SimpleUAM see it if run in
similar circumstances.

To print a specific configuration use:

```bash
pdm run suam-config print -c <config-id>
```

With `<config-id>` as one of the outputs from a `list-*` command.
This flag can be given multiple times in order to print multiple config files,
as follows:

```bash
pdm run suam-config print -c path -c auth
```

To print all the configurations use:

```bash
pdm run suam-config print --all
```

Add the `--resolved` flag to print the configurations after interpolations have
been applied.

**Arguments**:

- **`--config=STRING`/`-c STRING`** (Mandatory) : The config file to be printed
  out.
  "`STRING`" can be any of the output lines from the `list-*` subcommands.
  Can be given multiple times to print out multiple configs.
- **`--all`/`-a`**: This prints out a list of all the config file that
  are being read from lowest to highest priority.
  Only useful when called with `--config-dir=`.
- **`--resolved`/`-r`**: Instead of printing out the unevaluated interpolations,
  the default, resolve all the fields before printing.

### The `write` sub-command {#cli-write}

the `write` sub-command will write the currently loaded configuration to the
default configuration directory.
This is a good way to initialize the configuration files for a machine.
By default this will only write fully commented configuration files to disk.

To write out all config files to the default configuration directory use:

```bash
pdm run suam-config write
```

Individual and multiple config files can be specified in the same way as
`print`.


**Arguments**:

- **`--config=STRING`/`-c STRING`**: The config file to be written
  out.
  "`STRING`" can be any of the output lines from the `list-*` subcommands.
  Can be given multiple times to print out multiple configs.
- **`--no-comment`**: Don't comment the output files.
- **`--overwrite`/`-o`**: Don't skip files that exist, overwrite them with the
  new versions instead.
- **`--output=DIR`/`-u DIR`**: Write config files out to `DIR` instead of the
  default config directory.

### The `install` sub-command {#cli-install}

The `install` sub-command links or copies config files from a provided directory
to the default config directory.
Note that config files being copied must have names that match the ones from
[the `list-files` sub-command](#cli-list-files).

To symlink all the config files from `<dir>` into the config directory run:

```bash
pdm run suam-config install -i <dir>
```

To *copy* all the config files from `<dir>` into the config directory run:

```bash
pdm run suam-config install -i <dir> --no-symlink
```

To symlink individual files run:

```bash
pdm run suam-config install -i <file>
```

**Arguments**:

- **`--input=STRING`/`-i STRING`** (Mandatory): A config file or directory to
  copy into the default search location.
  If `STRING` is a directory the argument can only be given once, if a file
  then it can given multiple times.
- **`--no-symlink`**: Don't create symlinks, just copy the files over.
- **`--overwrite`/`-o`**: Don't skip files that exist, overwrite them with the
  new versions instead.

## Configuration Files {#files}

Some basic information on each config file

### `paths.conf.yaml` {#files-path}

Defines paths that SimpleUAM will use for caches, logs, data, etc...

Most people shouldn't need to change this.
Locations for more specific tasks are defined in their respective configuration
files and changing those should suffice.

Changes to this config will require reinstallation or rebuilding large portions
of a worker node.
Try to keep this static after initial setup.

#### Properties

- **Python Dataclass**: `simple_uam.util.config.path_config.PathConfig` ([API](../../reference/simple_uam/util/config/path_config/#simple_uam.util.config.path_config.PathConfig))
- **Purview Category**: Per-Machine
- **Config File Name**: `paths.conf.yaml`
- **Interpolation Key**: `path`

#### Contents

??? example "Default `paths.conf.yaml`"

    ```yaml
    --8<-- "docs/assets/config/paths.conf.yaml"
    ```

#### Key Fields

- **`config_directory`**: This will add another configuration directory to the
  chain of [overloaded config directories](#semantics-overloading).
  Try to avoid setting this without good reason.
- **`cache_directory`**: Location for files which are used in install and
  execution but can be regenerated after deletion.
- **`log_directory`**: Location to place any logs that are generated by
  SimpleUAM.
- **`work_directory`**: Location for files that are used as various SimpleUAM
  commands and programs run.
- **`data_directory`**: Location for static files that need to present at
  runtime but which aren't, usually, directly modified.

### `auth.conf.yaml` {#files-auth}

Authentication keys or tokens needed by a SimpleUAM install.

Try not to check this into a repo or make it public.

#### Properties

- **Python Dataclass**: `simple_uam.util.config.auth_config.AuthConfig`
  ([API](../../reference/simple_uam/util/config/auth_config/#simple_uam.util.config.auth_config.AuthConfig))
- **Purview Category**: Per-Deployment
- **Config File Name**: `auth.conf.yaml`
- **Interpolation Key**: `auth`

#### Contents

??? example "Default `auth.conf.yaml`"

    ```yaml
    --8<-- "docs/assets/config/auth_default.conf.yaml"
    ```

??? example "Example `auth.conf.yaml`"

    ```yaml
    --8<-- "docs/assets/config/auth.conf.yaml"
    ```

#### Key Fields

- **`isis_user`**: Either `null` or your username for the Isis GitLab instance.
- **`isis_token`**: Either `null` or an API token for the Isis GitLab instance.

### `corpus.conf.yaml` {#files-corpus}

The repositories and git refspecs used in an install of SimpleUAM.
These can be changed to specify the versions of any SWRi code used and
make a deployment more repeatable.

#### Properties

- **Python Dataclass**: `simple_uam.util.config.corpus_config.CorpusConfig`
  ([API](../../reference/simple_uam/util/config/corpus_config/#simple_uam.util.config.corpus_config.CorpusConfig))
- **Purview Category**: Per-Deployment
- **Config File Name**: `corpus.conf.yaml`
- **Interpolation Key**: `corpus`

#### Contents

??? example "Default `corpus.conf.yaml`"

    ```yaml
    --8<-- "docs/assets/config/corpus.conf.yaml"
    ```

#### Key Fields

- **`trinity`**: Defines the location and version of the trinity-craidl repo to
  copy example designs from.
- **`graphml_corpus`**: Defines where to find the graphml dump of the component
  and design corpus.
- **`creopyson`**: Defines where to find the python package with Creoson
  bindings.
- **`creoson_server`**: URLs for both API (GitLab Token) based and manual
  downloads of the modified creoson server used by direct2cad.
- **`direct2cad`**: Defines the location of the core direct2cad repo used for
  a deployment.

### `win_setup.conf.yaml` {#files-win-setup}

Options for packages to install on various windows nodes.

Should be left unchanged by most, this mainly exists to make larger scale
deployment easier to customize.

#### Properties

- **Python Dataclass**: `simple_uam.util.config.win_setup_config.WinSetupConfig`
  ([API](../../reference/simple_uam/util/config/win_setup_config/#simple_uam.util.config.win_setup_config.WinSetupConfig))
- **Purview Category**: Per-Deployment
- **Config File Name**: `win_setup.conf.yaml`
- **Interpolation Key**: `win_setup`

#### Contents

??? example "Default `win_setup.conf.yaml`"

    ```yaml
    --8<-- "docs/assets/config/win_setup.conf.yaml"
    ```

#### Key Fields

- **`global_dep_packages`**: Chocolatey packages to install on all node, please
  only add to this list.
- **`qol_dep_packages`**: QoL chocolatey packages.
- **`*_dep_packages`**: A list of chocolatey packages to install on the
  corresponding type of node.
  Please only add to this list.
- **`worker_pip_packages`**: Pip packages to be installed globally on the
  worker (as opposed to within a venv via PDM), needed for direct2cad.

### `craidl.conf.yaml` {#files-craidl}

Settings for working with a corpus DB or static corpus.

#### Properties

- **Python Dataclass**: `simple_uam.util.config.craidl_config.CraidlConfig`
  ([API](../../reference/simple_uam/util/config/craidl_config/#simple_uam.util.config.craidl_config.CraidlConfig))
- **Purview Category**: Per-Machine
- **Config File Name**: `craidl.conf.yaml`
- **Interpolation Key**: `craidl`

#### Contents

??? example "Default `craidl.conf.yaml`"

    ```yaml
    --8<-- "docs/assets/config/craidl.conf.yaml"
    ```

#### Key Fields

- **`example_dir`**: Location for saved example designs.
  Possibly better thought of as a static design corpus to live alongside the
  static component corpus.
- **`stub_server`**: Settings for running the TinkerPop server reference
  implementation with a provided graphml corpus dump.
   - **`graphml_corpus`**: The graphml corpus file to load on server start.
   - **`host`**: The host to *serve* the graph database to.
     `localhost` will only serve to clients on the same machine.
     `0.0.0.0` will serve to any client.
    - **`port`**: Port to server the database on.
    - **`read_only`**: Should the stub server allow writes? Note that even
      if `false` no writes will be persisted, the state of the DB is reset
      on each run.
- **`server_host`**: The corpus DB to *connect to* when generating info files or
  creating a static component corpus.
- **`server_port`**: The port of the corpus DB to connect to for various tasks.
- **`static_corpus`**: The static corpus to use when performing various tasks.
- **`static_corpus_cache`**: The location of the cache used when generating a
  *new* static corpus from the corpus DB.
- **`use_static_corpus`**: Use the static corpus when possible if `true`
  otherwise default to using a running corpus DB


### `d2c_workspace.conf.yaml` {#files-d2c-workspace}

Settings for the execution of direct2cad tasks on a worker node

#### Properties

- **Python Dataclass**: `simple_uam.util.config.d2c_workspace_config.D2CWorkspaceConfig`
  ([API](../../reference/simple_uam/util/config/d2c_workspace_config/#simple_uam.util.config.d2c_workspace_config.D2CWorkspaceConfig))
- **Purview Category**: Per-Deployment (mostly)
- **Config File Name**: `d2c_workspace.conf.yaml`
- **Interpolation Key**: `d2c_workspace`

#### Contents

??? example "Default `d2c_workspace.conf.yaml`"

    ```yaml
    --8<-- "docs/assets/config/d2c_workspace.conf.yaml"
    ```

#### Key Fields

- **`results_dir`**: The location to place analysis result zip files.
  Should be set to point to the results storage.
  If workers are different then use a symlink to the intended directory.
- **`results`**: Options on how to generate and store results.
    - **`max_count`**: Number of results to allow in `results_dir`.
      The oldest zip files will be deleted until the count is low enough.
      `-1` disables pruning entirely.
    - **`min_staletime`**: Time after last access to prevent the deletion
      of a record in seconds.
      Results that aren't stale enough will not be deleted even if there
      are more than `max_count`.

### `broker.conf.yaml` {#files-broker}

Settings that define how to connect to a message broker and backend.
It is used by both worker nodes and clients, and is very important to get
correct in order for a SimpleUAM deployment to function.

Thankfully, this is set up such that all the workers and clients should be able
to share a single file unless there's network or DNS weirdness.

#### Properties

- **Python Dataclass**: `simple_uam.util.config.broker_config.BrokerConfig`
  ([API](../../reference/simple_uam/util/config/broker_config/#simple_uam.util.config.broker_config.BrokerConfig))
- **Purview Category**: Per-Deployment
- **Config File Name**: `broker.conf.yaml`
- **Interpolation Key**: `broker`

#### Contents

??? example "Default `broker.conf.yaml`"

    ```yaml
    --8<-- "docs/assets/config/broker.conf.yaml"
    ```

#### Key Fields

- **`protocol`**: The protocol to use for the broker.
  Generally either `amqp` or `amqps` for RabbitMQ and `redis` for Redis.
- **`host`**: The IP or URL of the message broker.
- **`port`**: The port to connect to on the message broker.
- **`db`**: The Redis db if needed, this should include a beginning `/` if
  provided at all. (e.g. use `/0` instead of just `0`)
- **`url`**: The full url of the message broker including protocol host, port,
  and the like.

    !!! warning ""
        If provided then `protocol`, `host`, `port`, and `db` are ignored.
        Make sure that `url` contains all necessary information.

- **`backend`**: Settings for an optional Message Backend (used for completion
  notifications)
    - **`enabled`**: Set to `true` in order to enable the backend.
    - **`protocol`**: Protocol to use for the backend, the only supported option
      is `redis`.
    - **`host`**: The IP or URL of the message backend.
    - **`port`**: The port to connect to on the message backend.
    - **`db`**: The Redis db this should include a beginning `/` if
      provided at all. (e.g. use `/0` instead of just `0`)
    - **`url`**: The full url of the messag backend including protocol host, port,
      and the like.

        !!! warning ""
            If provided then `backend.protocol`, `backend.host`, `backend.port`, and `backend.db` are ignored.
            Make sure that `backend.url` contains all necessary information.


### `d2c_worker.conf.yaml` {#files-d2c-worker}

Settings for running the process that listens to the message broker for new
tasks, executes them via the workspace code, and potentially returns
confirmations or other information to a backend.

#### Properties

- **Python Dataclass**: `simple_uam.util.config.d2c_worker_config.D2CWorkerConfig`
  ([API](../../reference/simple_uam/util/config/d2c_worker_config/#simple_uam.util.config.d2c_worker_config.D2CWorkerConfig))
- **Purview Category**: Per-Machine
- **Config File Name**: `d2c_worker.conf.yaml`
- **Interpolation Key**: `d2c_worker`

#### Contents

??? example "Default `d2c_worker.conf.yaml`"

    ```yaml
    --8<-- "docs/assets/config/d2c_worker.conf.yaml"
    ```

#### Key Fields

- **`max_processes`**: The number of simultaneously running direct2cad processes.
  Due to limitations with Creoson the only supported number is `1`.
- **`max_threads`**: The number of threads, per-process, on which to run
  direct2cad tasks.
  The only currently supported value is `1`.
- **`shutdown_timeout`**: How long to wait for a worker to shutdown in
  milliseconds.
- **`skip_logging`**: Do we preserve the logs that dramatiq produces?
  Note that this does not effect the usual structlog based logging, just the
  logging from the library that manages a worker process.
- **`service`**: Settings for running the direct2cad worker as a service.
  These correspond closely to the corresponding settings in [NSSM](https://nssm.cc/usage).
