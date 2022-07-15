# Worker Node Setup

A worker can analyze designs on behalf of clients and requires access to a
license server and a broker for most tasks.

### Prerequisites {#prereqs}

- [General Setup](general.md) has been completed.
- Auth tokens, SSH keys, or credentials for `git.isis.vanderbilt.edu`
- A broker running at `<broker>`.
- Access to a corpus:
    - **Either:** Via a [corpus DB](graph.md) at `<corpus-db>`.
    - **Or:** A static corpus installed as described [here](corpus.md).
- Have a results directory set up at `<results-dir>`.
    - Ensure that it's readable and writable by the worker.
- Optionally have a backend running at `<backend>`.
- Optionally have `design_swri.json` files available for testing.
    - Try using the example store as described [here](../../usage/craidl/#examples)
      if no other source is available.

### Install Dependencies {#deps}

> Install utilities like wget and rsync, as well as global python packages
> needed by creopyson and direct2cad.

- Open an admin powershell to `<repo-root>`.
- Install dependencies:
  ```bash
  pdm run setup-win install.worker-deps
  ```
- Close powershell and open a new instance for future commands.

### Get License Information {#license}

**Option 1:** License Server

- Have a license server running at `<license-server.ip>` on
  port `<license-server.port>`.

**Option 2:** Static Creo License

- Open an admin powershell to `<repo-root>`.
- Get your mac address (for generating licenses):
  ```bash
  pdm run setup-win mac-address
  ```
- Save the result as `<creo-license.host-id>`.
- Get a node-locked license for `<creo-license.host-id>`.
- If using a local license, have the license file for the above mac
  address downloaded to `<creo-license.file>`.

### Install Creo {#creo}

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
  pdm run setup-win worker.disable-ieesc
  ```

### Install Creopyson {#creopyson}

> Creopyson provides a python interface to Creo.

- Prepare to connect to `git.isis.vanderbilt.edu`.
    - **Either:** Install auth tokens as in [General Setup](general.md).
    - **Or:** Install SSH keys for `git.isis.vanderbilt.edu`.
    - **Or:** have credentials ready for prompt.
- Open an admin powershell to `<repo-root>`.
- Download creopyson repository and install via pip:
    ```bash
    pdm run setup-win worker.creopyson
    ```
- Follow prompts.

### Configure Corpus Settings {#corpus}

> Performing various analysis tasks requires access to either a Corpus DB
> or a local static corpus.
> The config file at `<config-dir>/craidl.conf.yaml` specifies which of these
> use and how the connection is configured.

- Open admin powershell to `<repo-root>`.
- *(Optional)* View currently loaded config file:
  ```bash
  pdm run suam-config print --config=craidl -r
  ```

#### **Option 1:** Using a static corpus. {#corpus-static}

- No changes should be needed to config files.

#### **Option 2:** Using a remote corpus DB. {#corpus-db}

- Create or update `<config-dir>/craidl.md`:
    - Set `use_static_corpus` to `False`.
    - Set `server_host` to `<corpus-db,host`.
    - Set `server_port` to `<corpus-db.port>`.
- See the [config file guide](../usage/config.md) for more detailed
  instructions and information.

**Further details on using a static or database corpus can be found
in this [section](../usage/craidl.md)...**

### Configure Results Dir {#results}

> The results directory needs to be configured to point at the appropriate
> directory.

- Open admin powershell to `<repo-root>`.
- *(Optional)* View currently loaded config file:
  ```bash
  pdm run suam-config print --config=d2c_workspace -r
  ```
- Create or update the config at `<config-dir>/d2c_workspace.conf.yaml`:
    - Set `results_dir` to `<results-dir>`.
- See the [config file guide](../usage/config.md) for more detailed
  instructions and information.

**Further details on results storage and local worker node operations are
in [this page](../usage/workspaces.md)...**

### Initialize Reference Workspace {#reference}

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
- Follow prompts.

**For further details on workspace configuration, operation, and running analyses
locally see [this page](../usage/workspaces.md)...**

### Test the Worker Node *(Optional)* {#test}

> Run a simple test task, generating the info files for a design, in order to
> test the worker node's configuration.

- Have a valid design file (usually `design_swri.json`) at `<design-file>`.
- Open a shell to `<repo-root>`.
- Test generating design info files:
  ```bash
  pdm run d2c-workspace tasks.gen-info-files --input=<design-file>
  ```
  When finished this should place an archive in the `<results-dir>` with the
  generated info files.
- Test generating processing designs:
  ```bash
  pdm run d2c-workspace tasks.process-design --input=<design-file>
  ```
  When finished this should place an archive in the `<results-dir>` with the
  processed design.

### Configure Broker Settings {#broker}

> The worker process itself needs to be configured with how to connect to a
> message broker.

- Open admin powershell to `<repo-root>`.
- *(Optional)* View currently loaded config file:
  ```bash
  pdm run suam-config print --config=broker -r
  ```
- Create or update the config at `<config-dir>/broker.conf.yaml`:
    - Set up the broker:
        - If you have a `<broker.url>`:
            - Set `url` to `<broker.url>`.
        - Otherwise:
            - Set `host` to `<broker.ip>`.
            - Set `protocol` to `"amqp"` if using RabbitMQ or `"redis"` if
              using Redis.
            - Set `port` to `<broker.port>`.
            - Set `db` to `<broker.db>` if you have one.
    - Set up the backend, if available:
        - Set `backend.enabled` to `true`
        - If you have a `<backend.url>`:
            - Set `broker.url` to `<broker.url>`
        - Otherwise:
            - Set `backend.host` to `<backend.ip>`.
            - Set `backend.port` to `<broker.port>`.
            - Set `backend.db` to `<broker.db>` if you have one.
- See the [config file guide](../usage/config.md) for more detailed
  instructions and information.

**Further details on configuring the worker's backend are
[here](../usage/workers.md)...**

### Run the Worker Node as a Process *(Optional)* {#run}

> You can run the worker node as a process to verify all the above settings
> function as intended.

- Open admin powershell to `<repo-root>`.
- Run the SimpleUAM worker node process:
  ```bash
  pdm run suam-worker run
  ```

!!! Note ""
    If the worker node process is running and the broker is correctly configured
    then the worker is also a valid client.
    This means that, if there is only one attached worker, you can run a basic
    round trip test of the system using [the instructions for testing the
    client node](../client/#test).

### Configure the Worker Node to Auto-Start on Boot *(Optional)* {#restart}

> The worker node service needs to configured, in particular whether it should
> automatically start on boot.

- Open admin powershell to `<repo-root>`.
- *(Optional)* View currently loaded config file:
  ```bash
  pdm run suam-config print --config=d2c_worker -r
  ```
- Create or modify the config at `<config-dir>/d2c_worker.conf.yaml`:
    - Set `service.auto_start` to `True`
- See the [config file guide](../usage/config.md) for more detailed
  instructions and information.

**Further details on configuring the worker as a service are
[here](../usage/workers.md)...**

### Set up the Worker Node Service {#service}

> We use [Non-Sucking Service Manager](https://nssm.cc) to manage the worker
> node service, and that requires some setup.

- Open admin powershell to `<repo-root>`.
- Install the SimpleUAM worker service:
  ```bash
  pdm run suam-worker service.install
  ```

### Start the Worker Node Service *(Optional)* {#service-start}

> The worker node service can start immediately but we recommend holding off
> until you've verified configurations while running the node as a process.

- Open admin powershell to `<repo-root>`.
- Install the SimpleUAM worker service:
  ```bash
  pdm run suam-worker service.start
  ```

**Further details on running the worker as a service are [here](../usage/workers.md)...**

### Next Steps {#next}

**View information on corpus use [here](../usage/craidl.md)...**<br/>
**View information on local task processing [here](../usage/workspaces.md)...**<br/>
**View information on remote task processing [here](../usage/workers.md)...**<br/>
