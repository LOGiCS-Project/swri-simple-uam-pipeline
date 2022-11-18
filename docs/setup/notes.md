# Installation Notes

The rest of the installation instructions share some basic elements of structure
that we will go over in this section.

## Multiple-Choice Steps {#step-choice}

While most steps in the install process are mandatory, some steps provide
multiple options for how to complete them.
They'll be formatted as follows, with an "Option" before the step number.

> ### Option 1.a) One Version of Step
>
> *...*
>
> ### Option 1.b) Another Version of Step
>
> *...*

In these cases, you should only follow instructions one of the options.

## Recommended Steps {#step-recommended}

Likewise, some steps in the instructions are only recommended and can be
skipped if desired.
Those steps will be have a "Recommended" tag after the step name, as in
the example below>

> ### 1) Step That's Not Required *(Recommended)*
>
> *...*

These steps are usually tests to validate that previous steps worked and can
be safely skipped.

## Placeholder Conventions {#placeholder}

Throughout these install instructions, but especially in the AWS setup,
we use placeholders like `<this-one>` to represent values that will be useful
later or which you, the user, should provide.
In either case, this information should be saved somewhere for future reference.

This guide tries to proactive about asking you to save potentially useful
information.
We recommend keeping a file open for this.

??? example "Example placeholder file from partway through AWS setup."
    ```yaml
    aws-vpc:
      prefix: example
      name: example-vpc
      id: vpc-XXXXXXXXXXXXXXXXX

    aws-public-subnet:
      name: example-public1-XX-XXXX-XX
      id: subnet-XXXXXXXXXXXXXXXXX

    aws-private-subnet:
      name: example-private1-XX-XXXX-XX
      id: subnet-XXXXXXXXXXXXXXXXX
      group:
        name: example-private-group

    aws-elastic-ip:
      name: example-eip-XX-XXXX-XX
      addr: 0.0.0.0
      id: eipassoc-XXXXXXXXXXXXXXXXX
    ```

We never use this information programmatically, so use whatever format you want,
but it does make it easier to keep track of what you're doing during install.
This is particularly important if you are setting up multiple machines and
don't want to waste time.

## 3) Command Line Interfaces {#cli}

All the command line scripts SimpleUAM provides are made using
[Invoke](https://www.pyinvoke.org/) and evaluated within a
[PDM](https://pdm.fming.dev/latest/) administered python environment.

This means that all the SimpleUAM provided commands must be run from
the root of the SimpleUAM repo (hereafter `<repo-root>`) and have this format:

```bash
pdm run <command>
```

The core `<command>`s are split between general commands, for use on both
clients and workers:

- `suam-config`: Which manages config files and configuration state.
- `craidl`: Which has tools for manipulating the component and design corpus.
- `suam-client`: Which provides a CLI for making requests to a worker deployment.

And worker `<command>`s, which deal with worker-only tasks like installation and
local evaluation requests:

- `setup-win`: Is the entry point for all the setup scripts.
- `d2c-workspace`: Which manages direct2cad evaluation environments.
- `fdm-workspace`: Which manages flight dynamics model build and evaluation
  environments.
- `suam-worker`: Which handles the worker-node server process.

All of these commands have `<sub-command>`s for individual tasks within them.
They can be listed with:

```bash
pdm run <command> --help
```

Each individual sub-command has detailed information on function and arguments
which can be accessed with:

```bash
pdm run <command> <sub-command> --help
```

Finally, these subcommands are run with:

```bash
pdm run <command> <sub-command> [ARGS]
```

## 4) Errors and Idempotence {#errors}

The install process is designed to be as idempotent as possible so that
mistakes can be fixed by repeating steps, starting by fixing the mistake
and proceeding onwards.

This is true enough that the update process is usually just running a few
key install steps with new inputs.

In some cases, scripts will check for whether a task has already been completed
and skip it if so.
These scripts usually have a flag to override this behavior which can be found
by looking at the documentation with the `--help` argument.

## 5) Configuration {#config}

SimpleUAM uses an internal configuration system based on
[OmegaConf](omegaconf.readthedocs.io/).
It reads YAML files in a platform specific directory for settings that are
used throughout the system.
While you can find a more detailed breakdown of the system [here](../usage/config.md),
this is a quick overview.

### 5.1) Configuration File Directory {#config-dir}

(TODO: fix) Once the SimpleUAM project is installed (in [General Setup](general.md)) you
can run the following command to find the config file directory:

```bash
pdm run suam-config dir
```

Files placed there will be loaded when most SimpleUAM code is started up.
The configuration is immutable for the runtime of a program and changes will
require a restart to register.

### 5.2) Configuration State {#config-state}

You can get a printout of the current configuration state with the following:

```bash
pdm run suam-config print --all
```

??? example "Sample Output of `pdm run suam-config print --all`"

    ```yaml
    --8<-- "docs/assets/config/print_all.conf.yaml"
    ```

If you want to see the full expanded version of the configs, with
all the [interpolations](https://omegaconf.readthedocs.io/en/2.1_branch/usage.html#variable-interpolation)
resolved, add the `--resolved` flag.

??? example "Sample Output of `pdm run suam-config print --all --resolved`"

    ```yaml
    --8<-- "docs/assets/config/print_all_resolved.conf.yaml"
    ```

### 5.3) Generating Stub Config Files {#config-write}

You can also use the `write` subcommand to write sample config files out to
the appropriate locations.
Run the following for more info:

```bash
pdm run suam-config write --help
```

### 5.4) Installing Config Files {#config-install}

The `install` subcommand will symlink or copy config files from another
location into the configuration directory for you.
This is useful if you want to share config files between worker nodes or
rapidly update a deployment.
Run the following for more info:

```bash
pdm run suam-config install --help
```

### 5.5) Config File Format {#config-format}

Config files can be partial and do not need to define every possible key.
Keys that are missing will just use their default values.

??? example "Overriding Configuration Fields."
    Consider the following defaults for `example.conf.yaml`:
    ```yaml
    ### example.conf.yaml defaults ###
    subsection:
        subfield-1: 'default'
        subfield-2: 'default'
    field-1: 'default'
    field-2: 'default'
    ```
    With the following `example.conf.yaml` actually on disk:
    ```yaml
    ### example.conf.yaml defaults ###
    subsection:
        subfield-2: 'modified'
    field-1: 'modifed'
    ```
    The final loaded values for `example.conf.yaml` as seen by the application
    would be:
    ```yaml
    ### example.conf.yaml defaults ###
    subsection:
        subfield-1: 'default'
        subfield-2: 'modified'
    field-1: 'modified'
    field-2: 'default'
    ```

When describing keys in a config file, we'll use dot notation.

??? example "Config File Dot Notation"
    Consider the following config file:
    ```yaml
    subsection:
        subfield-1: 'sub-1'
        subfield-2: 'sub-2'
    field-1: 'fld-1'
    field-2: 'fld-2'
    ```
    Then `field-1` would have value `'fld-1'` and `subsection.subfield-1` would
    have value `'sub-1'`

    Likewise, setting `foo` to `3` and `bar.buzz` to `4` would leave you
    with the following file:
    ```yaml
    foo: 3
    bar:
        buzz: 4
    ```

**TODO: Further details are [here](../usage/config.md)...**

## 6) Next Steps

TODO : If client & deployment admin has given you instructions go to client
TODO : If deployment (either local or remote) go to deployment
