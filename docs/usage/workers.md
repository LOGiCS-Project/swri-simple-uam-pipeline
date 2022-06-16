# Direct2Cad Worker

- Worker runs as a service and listens for tasks from msg broker.
    - When task arrives uses the D2C Workspaces code to run the analysis and
      produce a result archive.
- Talk about broker vs backend.
    - Broker gets message from client to worker.
    - Backend gets notification of completion from worker to client. (Really
      just tells you the name of the zip file from a particular request.)
    - RabbitMQ: Broker only
    - Redis: Both Broker and Backend
- Supports running worker node as normal process:
    - Normal Process: `pdm run suam-worker run`
- Supports running worker node as a service managed by NSSM. The commands do the
  obvious things.
    - `pdm run suam-worker service.install`
    - `pdm run suam-worker service.uninstall`
    - `pdm run suam-worker service.configure` : Converts config file settings to
      NSSM settings.
    - `pdm run suam-worker service.start`
    - `pdm run suam-worker service.stop`
    - `pdm run suam-worker service.restart`
    - `pdm run suam-worker service.status`
- Talk about config file `broker.conf.yaml` and fields:
    - Broker config
    - Backend config
- Talk about config file `d2c_worker.conf.yaml` and fields:
    - Worker Node Opts
    - Service config

??? todo "reqs"
    - Workers:
        - Configuring broker and backend
        - Configure use as service
        - Remote task processing

A worker will listen for tasks from a message broker and then run those tasks.

### Configure Worker Settings

- Configure the message broker settings in
  `<config-dir>/broker.conf.yaml`.
- Configure the settings in
  `<config-dir>/d2c_worker.conf.yaml`.
- Examine loaded config with `pdm run suam-config print --config=d2c_worker -r`

### Run Worker Process

A worker node, which listens to a broker and performs tasks as requests come
in must have been set up as [here](../setup/worker.md).

- Make sure that direct2cad workspaces have been properly set up on this node
  as described [here](workspaces.md).
    - That code is what the worker process uses to evaluate a task, so if it
      doesn't function locally it won't function when a remote client asks.
- Make sure that a message broker is running at the configured host and port.

Actually run the worker process.

- In admin powershell at `<repo-root>`.
    - Run: `pdm run suam-worker worker.run`

Note that this is a process not a service. If it shuts down it needs to be
restarted.
