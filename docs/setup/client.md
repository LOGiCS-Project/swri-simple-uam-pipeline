# Client Node Setup

Clients send design analysis requests to a message broker so that worker
nodes can process them.

Unlike the other nodes clients can easily be of any platform as long as they
can access the same brokers and results directory as the workers.

## Prerequisites {#prereq}

- An auth token, SSH keys or credentials for `git.isis.vanderbilt.edu`.
- A broker running at `<broker>`.
- Optionally, a backend running at `<backend>`.
- The following installed software:
    - Git
    - Python (>=3.9, <3.11)
- An environment with the following Python packages:
    - [PDM](https://pdm.fming.dev/latest/)

## Setup File Sharing *(Optional)* {#files}

If you intend to share files (e.g. results) between workers and clients then
set that up now, if you haven't done so already.

If using AWS the instructions for the FSx file share take care of this.

Otherwise shared directory and file server configurations are too varied for us
to provide precise instructions.
The only real requirement is that worker nodes see the shared file storage as
a normal directory.

- Save the shared results directory as `<results-dir>`.

## Download SimpleUAM {#download}

> Get this repo onto the machine somehow, cloning is the default method.
> If you have a shared drive, placing the repo there will allow local development
> without constant pushing and pulling.

- Save the repo's final location as `<repo-root>`.

### **Option 1:** Clone from Github (HTTP): {#download-github-http}

```bash
git clone https://github.com/LOGiCS-Project/swri-simple-uam-pipeline.git <repo-root>
```

### **Option 2:** Clone from Github (SSH): {#download-github-ssh}

```bash
git clone git@github.com:LOGiCS-Project/swri-simple-uam-pipeline.git <repo-root>
```

## Initialize SimpleUAM Package {#init}

> Initialize pdm and packages for client use.

- Navigate a shell to `<repo-root>`.
- Setup PDM environment for this repo:
  ```bash
  pdm install
  ```
- Test whether setup script was installed:
  ```bash
  pdm run suam-client --help
  ```
  Result should be a help message showing all of `suam-client`'s flags and
  sub-commands.

## Get Configuration Directory {#config}

> The configuration directory holds `*.conf.yaml` files that determine how
> many aspects of a running SimpleUAM system operate.

- Navigate a shell to `<repo-root>`.
- Print config directory:
  ```bash
  pdm run suam-config dir
  ```
- Save result as `<config-dir>`.

## Configure Broker Settings {#broker}

> The client process needs to be configured with how to connect to a
> message broker.
> These options should be identical to any worker nodes which is why they
> use the same config file.

### **Option 1:** Use the worker `broker.conf.yaml` {#broker-reuse}

> As long as the IPs or DNS names of the broker and backend resolve to the
> same machines as the worker, then you can reuse the `broker.conf.yaml`
> directly.

- Have the worker's `broker.conf.yaml` accessible at `<conf-loc>`.
- Make a copy in the configuration directory:
  ```bash
  pdm run suam-config install --no-symlink --input=<conf-loc>
  ```

**See the [config file usage page](../../usage/config#cli-install) for other
ways to set this up...**

### **Option 2**: Create a new configuration {#broker-new}

> If visibility of the broker and backend differs from the default then
> a client specific `broker.conf.yaml` needs to be created.

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
- See the [config file guide](../../usage/config#files-broker) for more detailed
  instructions and information.

**Further details on configuring the client's broker and backend are
[here](../usage/clients.md)...**

## Test the Client Node *(Optional)* {#test}

> Run a simple test task, generating the info files for a design, in order to
> test the client node's configuration.

- Have a valid design file (usually `design_swri.json`) at `<design-file>`.
- Have a broker running at the configured location.
- Have at least one worker running and connected to the broker.
- Open a shell to `<repo-root>`.
- Test generating design info files:
  ```bash
  pdm run suam-client direct2cad.gen-info-files --input=<design-file>
  ```
  A worker should pick up this task and run it, eventually placing an archive
  in the `<results-dir>` with the generated info files.
- Test generating processing designs:
  ```bash
  pdm run suam-client direct2cad.process-design --input=<design-file>
  ```
  A worker should pick up this task and run it, eventually placing an archive
  in the `<results-dir>` with the generated results.


**Information on how to run a fill analysis pipeline, through either a
CLI or Python code, can be found [here](../usage/clients.md)...**
