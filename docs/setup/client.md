# Worker Node Setup

A worker can analyze designs on behalf of clients and requires access to a
license server and a broker for most tasks.

### Prerequisites

- [General Setup](general.md) has been completed.
- SSH keys or credentials for `git.isis.vanderbilt.edu`
- A broker running at `<broker-ip>` and `<broker-port>`
- Access to a corpus:
    - **Either:** Via a [corpus DB](graph.md) at `<corpus-db-ip>` on port `<corpus-db-port>`
    - **Or:** A static corpus installed as described [here](corpus.md).
- Have a results directory set up at `<results-dir>`.

### Install Dependencies

> Install utilities like wget and rsync.

- Open an admin powershell to `<repo-root>`.
- Install dependencies:
  ```bash
  pdm run setup-win install.worker-deps
  ```

### Get License Information

**Option 1:** License Server

- Have a license server running at `<license-server-ip>` on port `<license-server-port>`.

**Option 2:** Static Creo License

- Open an admin powershell to `<repo-root>`.
- Get your mac address (for generating licenses):
  ```bash
  pdm run setup-win mac-address
  ```
- If using a local license, have the license file for the above mac
  address downloaded somewhere convenient.

### Install Creo

> Downloads and installs PTC Creo 5.6.

- Open an admin powershell to `<repo-root>`.
- Download and run installer:
  ```bash
  pdm run setup-win worker.creo
  ```
- Read instructions in terminal and hit enter when ready.
- Follow installer prompts until done.

> Fix some minor usability issues.

- If on Windows Server 2019 you can disable the IE Enhanced Security popups
  that open whenever Creo starts.
  ```bash
  pdm run setup worker.disable-ieesc
  ```

### Install Creopyson

> Creopyson provides a python interface to Creo.

- Prepare to connect to `git.isis.vanderbilt.edu`.
    - **Either:** Install SSH keys for `git.isis.vanderbilt.edu`.
    - **Or:** have credentials ready for prompt.
- Open an admin powershell to `<repo-root>`.
- Download creopyson repository and install via pip:
    ```bash
    pdm run setup-win worker.creopyson
    ```
- Follow prompts.

### Configure Corpus Settings

> Performing various analysis tasks requires access to either a Corpus DB
> or a local static corpus.
> The config file at `<config-dir>/craidl.conf.yaml` specifies which of these
> use and how the connection is configured.

- Open admin powershell to `<repo-root>`.
- *(Optional)* View currently loaded config file:
  ```bash
  pdm run suam-config print --config=craidl -r
  ```

#### **Option 1:** Using a static corpus.

- No changes should be needed to config files.

#### **Option 2:** Using a remote corpus DB.

- Update `<config-dir>/craidl.md`:
    - Set `use_static_corpus` to `False`.
    - Set `server_host` to `<corpus-db-host`.
    - Set `server_port` to `<corpus-db-port>`.
- See the [config file guide](../usage/configuration.md) for more detailed
  instructions and information.

**Further details on using a static or database corpus can be found
in this [section](../usage/craidl.md)...**

### Configure Results Dir

> The results directory needs to be configured to point at the appropriate
> directory.

- Open admin powershell to `<repo-root>`.
- *(Optional)* View currently loaded config file:
  ```bash
  pdm run suam-config print --config=d2c_workspace -r
  ```
- Update the config at `<config-dir>/d2c_workspace.conf.yaml`:
    - Set `results_dir` to `<results-dir>`.
- See the [config file guide](../usage/configuration.md) for more detailed
  instructions and information.

**Further details on results storage and local worker node operations are
in [this page](../usage/workspaces.md)...**

### Initialize Reference Workspace

> Each worker needs a pristine copy of the workspace in which designs can be
> analyzed.
> This reference workspace will be copied, via rsync for efficiency, whenever
> the worker performs a new analysis.
> The results archives are also constructed by gathering all the files which
> have been changed after an analysis when compared to the reference directory.

- Open admin powershell at `<repo-root>`.
- Set up the reference workspace:
  ```bash
  pdm run d2c-workspace setup.reference-workspace
  ```

**For further details on workspace configuration, operation, and running analyses
locally see [this page](../usage/workspaces.md)...**

### Configure Worker Settings

> The worker process itself needs to be configured with how to connect to a
> message broker.

- Open admin powershell to `<repo-root>`.
- *(Optional)* View currently loaded config file:
  ```bash
  pdm run suam-config print --config=d2c_worker -r
  ```
- Update the config at `<config-dir>/d2c_worker.conf.yaml`:
    - Set `broker.protocol` to `"amqp"` if using RabbitMQ or `"redis"` if
      using Redis.
    - Set `broker.host` to `<broker-ip>`.
    - Set `broker.port` to `<broker-port>`.
    - If using Redis, set `broker.db` to `<broker-db>`
- See the [config file guide](../usage/configuration.md) for more detailed
  instructions and information.

**Further details on configuring the worker's backend are
[here](../usage/workers.md)...**

### Run the Worker Node as a Process *(Optional)*

> You can run the worker node as a process to verify all the above settings
> function as intended.

- Open admin powershell to `<repo-root>`.
- Run the SimpleUAM worker node:
  ```bash
  pdm run d2c-worker run
  ```

### Configure the Worker Node to Auto-Start on Boot *(Optional)*

> The worker node service needs to configured, in particular whether it should
> automatically start on boot.

- Open admin powershell to `<repo-root>`.
- *(Optional)* View currently loaded config file:
  ```bash
  pdm run suam-config print --config=d2c_worker -r
  ```
- Edit the config at `<config-dir>/d2c_worker.conf.yaml`:
    - Set `service.auto_start` to `True`
- See the [config file guide](../usage/configuration.md) for more detailed
  instructions and information.

**Further details on configuring the worker as a service are
[here](../usage/workers.md)...**

### Set up the Worker Node Service

> We use [Non-Sucking Service Manager](https://nssm.cc) to manage the worker
> node service, and that requires some setup.

- Open admin powershell to `<repo-root>`.
- Install the SimpleUAM worker service:
  ```bash
  pdm run d2c-worker service.install
  ```

### Start the Worker Node Service *(Optional)*

> The worker node service can start immediately but we recommend holding off
> until you've verified configurations while running the node as a process.

- Open admin powershell to `<repo-root>`.
- Install the SimpleUAM worker service:
  ```bash
  pdm run d2c-worker service.start
  ```

**Further details on running the worker as a service are [here](../usage/workers.md)...**

### Next Steps

**View information on corpus use [here](../usage/craidl.md)...**<br/>
**View information on local task processing [here](../usage/workspaces.md)...**<br/>
**View information on remote task processing [here](../usage/workers.md)...**<br/>
