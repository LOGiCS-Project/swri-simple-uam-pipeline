# Client Node Setup

Clients send design analysis requests to a message broker so that worker
nodes can process them.

Unlike the other nodes clients can easily be of any platform as long as they
can access the same brokers and results directory as the workers.

### Prerequisites

- SSH keys or credentials for `git.isis.vanderbilt.edu`.
- A broker running at `<broker-ip>` and `<broker-port>`.
- The following installed software:
    - Git
    - Python (>=3.9, <3.11)
- An environment with the following Python packages:
    - [PDM](https://pdm.fming.dev/latest/)

### Setup File Sharing *(Optional)*

If you intend to share files (e.g. results) between workers and clients then
set that up now, if you haven't done so already.

If using AWS the instructions for the FSx file share take care of this.

Otherwise shared directory and file server configurations are too varied for us
to provide precise instructions.
The only real requirement is that worker nodes see the shared file storage as
a normal directory.

- Save the shared results directory as `<results-dir>`.

### Download SimpleUAM

> Get this repo onto the machine somehow, cloning is the default method.
> If you have a shared drive, placing the repo there will allow local development
> without constant pushing and pulling.

- Save the repo's final location as `<repo-root>`.

#### **Option 1:** Clone from Github (HTTP):

```bash
git clone https://github.com/LOGiCS-Project/swri-simple-uam-pipeline.git <repo-root>
```

#### **Option 2:** Clone from Github (SSH):

```bash
git clone git@github.com:LOGiCS-Project/swri-simple-uam-pipeline.git <repo-root>
```

### Initialize SimpleUAM Package

> Initialize pdm and packages for client use.

- Navigate a shell to `<repo_root>`.
- Setup PDM environment for this repo:
  ```bash
  pdm install
  ```
- Test whether setup script was installed:
  ```bash
  pdm run d2c-client --help
  ```
  Result should be a help message showing all of `d2c-client`'s flags and
  subcommands.

### Get Configuration Directory

> The configuration directory holds `*.conf.yaml` files that determine how
> many aspects of a running SimpleUAM system operate.

- Navigate a shell to `<repo_root>`.
- Print config directory:
  ```bash
  pdm run suam-config dir
  ```
- Save result as `<config-dir>`.

### Configure Broker Settings

> The client process needs to be configured with how to connect to a
> message broker.
> These options should be identical to any worker nodes which is why they
> use the same config file.

- Open a shell to `<repo-root>`.
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
- See the [config file guide](../usage/config.md) for more detailed
  instructions and information.

**Further details on configuring the client's broker and backend are
[here](../usage/clients.md)...**

### Test the Client Node *(Optional)*

> Run a simple test task, generating the info files for a design, in order to
> test the client node's configuration.

- Have a valid design file (usually `design_swri.json`) at `<design-file>`.
- Have a broker running at the configured location.
- Have at least one worker running and connected to the broker.
- Open a shell to `<repo-root>`.
- Test generating design info files:
  ```bash
  pdm run d2c-client gen-info-files --input=<design-file>
  ```
  A worker should pick up this task and run it, eventually placing an archive
  in the `<results-dir>` with the generated info files.

**Information on how to run a fill analysis pipeline, through either a
CLI or Python code, can be found [here](../usage/clients.md)...**
