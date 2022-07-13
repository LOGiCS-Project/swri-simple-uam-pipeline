# SimpleUAM Installation Guide

!!! info

    We would appreciate assistance in making this guide better.
    Any notes on issues with the install process, lack of clarity in wording,
    or other improvements would be appreciated.

<figure markdown>
  ![Project Components](../assets/component-diagram.png)
  <figcaption>SimpleUAM Component Structure</figcaption>
</figure>

The core goal of SimpleUAM is allow users to set up a service for processing
requests to analyze UAM and UAV designs.
Client nodes, such as optimizers or search tools, should be able to queue
requests for distribution to worker nodes as they become available.
The results of those analyses, packaged as zip files, should then be made
available to the clients as they're completed.

The key components of a SimpleUAM deployment are:

- **Client Nodes**: These make requests to analyze designs and retrieve analysis
  results once they finish.
  Client nodes will usually be running some optimization or search process.
- **Message Brokers**: These gather analysis requests from client nodes and
  distribute them to free worker nodes.
- **Worker Nodes**: These will perform analyses on designs and store the results
  somewhere accessible to the clients.
- **License Management**: Each worker node needs Creo to perform analysis, and
  a license for Creo must be made available somehow.
    - **License Server**: These can provide licenses to a number of worker nodes
      at once if provided with a floating license.
    - **Node-Locked Creo License**: This is a worker-specific, static license
      file that can be placed on a worker.
- **Component Corpus**: A corpus of component information that every
  worker needs in order to analyze designs.
    - **Corpus DB**: A graph database that the worker can use to look up
      component information.
    - **Static Corpus**: A static file containing a dump of the component corpus
      which is placed on each worker node.
- **Results Storage**: A file system, accessible to both worker nodes and
  clients, where analysis results (in individual zip files) are placed.
- **Results Backends**: These notify client nodes when their analysis requests
  are completed and where the output is in Results Storage.

In order to form a complete SimpleUAM deployment some core requirements need to
be met:

- There must be one, and only one, message broker.
    - The broker must be accessible over the network to all worker and client nodes.
- There needs to be at least one configured, running worker node to run analyses.
    - Each worker node needs to have a Creo license, either through a
      node-locked license or a connection to a Creo license server.
    - Each worker node needs to have access to a component corpus, either through
      an initialized corpus DB or a static corpus file.
- There must be a results storage accessible to all the worker and client nodes.
    - The results storage should be a directory where workers can place files
      which are then made accessible to all the clients,
    - Generally these are network file share or some local folders with
      automatic synchronization mechanism like rsync+cron or Dropbox.
- In order for clients to receive analysis completion notifications there must
  be a single, unique results backend.
    - This backend must be accessible over the network to all worker nodes and
      any client that wants to receive notifications.
    - Note that a results backend is optional and simply polling the results
      storage is perfectly viable.

With a SimpleUAM deployment meeting those requirements, a client nodes can
offload analysis jobs to a pool of workers though simple python and command
line interfaces.

## Choosing a Service Topology {#topology}

It's possible to distribute SimpleUAM components between multiple machines
in numerous ways that meet the given requirements.
Picking a topology, specifically the components that go on each individual
machine, tells you which installation steps are needed for that machine.

We'll look at two example topologies, one I use for (semi)local development
work and one for a potential production system.

<figure markdown>
  ![Project Components](../assets/development-setup.png)
  <figcaption>Development SimpleUAM System</figcaption>
</figure>

This development setup has a local machine and a single worker.
The local machine is set up so it can run a SimpleUAM client and so that any
code shared with a worker node can be edited in whatever manner the user is
comfortable with.
The worker node, running in a VM, then has all the other necessary components of
the service, including broker, license, and corpus.

The structure is a broad guideline and can be tweaked as needed.
For instance, if you're running windows you can just run all the components on
your local machine and use a stub message broker that will run analysis requests
as blocking calls.
Alternately, the worker node can be running on a server somewhere with a NFS
shared drive acting as the shared folder.

<figure markdown>
  ![Project Components](../assets/production-setup.png)
  <figcaption>Production SimpleUAM System</figcaption>
</figure>

The production service has significantly more going on.
There are one or more clients producing analysis requests, multiple workers
processing them, a Creo license server, a message broker, a results backend,
and results storage.

This setup can scale relatively easily while providing features like completion
notifications.
In fact this is the intended topology for the AWS instructions, with clients
either accessing the other components via a VPN or simply running directly
on the cloud.

Other topologies are also viable, for instance running a central graph database
for all the workers to share instead of relying on a local, static corpus.

The **most important part** of choosing a service topology is knowing what
component(s) are going to be running on each individual server or VM.
Given that one can just go through the instructions for each component on
a machine in sequence, repeating that process for each machine in the
deployment.

## Command Line Interfaces {#cli}

All the command line scripts SimpleUAM provides are made using
[Invoke](https://www.pyinvoke.org/) and evaluated within a
[PDM](https://pdm.fming.dev/latest/) administered python environment.

This means that all the SimpleUAM provided commands must be run from
`<repo-root>` and have this format:

```bash
pdm run <command>
```

All the core SimpleUAM commands `suam-config`, `setup-win`, `craidl`,
`d2c-workspace`, and `d2c-client` will print a help message when run without
arguments.
In their base form these commands are safe and will never make change to your
system.
The help messages also provide a list of subcommands that do perform
various tasks.

These subcommands are run with:

```bash
pdm run <command> <sub-command> [ARGS]
```

All of these subcommands come with detailed help information that can be
accessed with:

```bash
pdm run <command> <sub-command> --help
```

These help messages are worth checking for available options and notes.

## Configuration {#config}

SimpleUAM uses an internal configuration system based on
[OmegaConf](omegaconf.readthedocs.io/).
It reads YAML files in a platform specific directory for settings that are
used throughout the system.
While you can find a more detailed breakdown of the system [here](../usage/config.md),
this is a quick overview.

### Configuration File Directory {#config-dir}

Once the SimpleUAM project is installed (in [General Setup](general.md)) you
can run the following command to find the config file directory:

```bash
pdm run suam-config dir
```

Files placed there will be loaded when most SimpleUAM code is started up.
The configuration is immutable for the runtime of a program and changes will
require a restart to register.

### Configuration State {#config-state}

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

### Generating Stub Config Files {#config-write}

You can also use the `write` subcommand to write sample config files out to
the appropriate locations.
Run the following for more info:

```bash
pdm run suam-config write --help
```

### Installing Config Files {#config-install}

The `install` subcommand will symlink or copy config files from another
location into the configuration directory for you.
This is useful if you want to share config files between worker nodes or
rapidly update a deployment.
Run the following for more info:

```bash
pdm run suam-config install --help
```

### Config File Format {#config-format}

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

**Further details are [here](../usage/config.md)...**

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

## AWS Network Setup {#setup-aws-net}

If you are using AWS you can start with our instructions for setting up a
virtual private cloud (VPC).
It sets up a private subnet for non-client machines and a VPN and Network drive
for access to that private subnet.

- **[AWS (Network) Setup](aws-network.md)**

## Machine Setup {#setup-machine}

Installation for each machine requires following the other pages in this section
in order, skipping any that aren't relevant and always including general setup.
Try to setup machines with centralized functions, like the license server and
message broker, before the worker nodes.

- **[AWS (Instance) Setup](aws-instance.md)**
- **[General Setup](general.md)** *(Required)*
- **[Creo License Server](license_server.md)**
- **[Message Broker & Results Backend](broker.md)**
- **[Corpus DB](graph.md)**
- **[Static Corpus](corpus.md)**
- **[Worker Node](worker.md)**

Client nodes are less directly dependent on the SimpleUAM infrastructure and their
setup can skip directly to the corresponding section:

- **[Client Node](client.md)**
