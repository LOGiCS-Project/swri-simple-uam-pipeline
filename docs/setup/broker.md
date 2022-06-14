# Message Broker Setup

A message broker allows worker nodes to pull analysis requests from a shared
queue.
The standard message broker is [RabbitMQ](https://www.rabbitmq.com/) with
the default settings.

## **Option 1:** Run RabbitMQ on a Linux Machine *(Recommended)*

> RabbitMQ is a backendless message broker that's sufficient if you're okay
> with clients not being notified when the analysis result
> is complete. (It will just appear in the results directory.)

- Follow the instructions [here](https://www.rabbitmq.com/download.html) to
  set up RabbitMQ.

- Save this machine's IP as: `<broker-ip>`
- Save rabbitmq's open port as: `<broker-port>` (default: 5672)

## **Option 2:** Run Redis on a Linux Machine

> Redis can be configured as a response backend as well as a message broker.
> This means that clients can get notified when an analysis is complete.

We have not tried to get this running so don't have install instructions.

- Save this machine's IP as: `<broker-ip>`
- Save redis's open port as: `<broker-port>` (default: 6379)
- Save the redis database you're using as: `<broker-db>` (default: "0")

## **Option 3:** Run RabbitMQ as a Windows Service

> This runs RabbitMQ as a windows service and is fine for development or
> production setups.

### Prerequisites

- [General Setup](general.md) has been completed.

### Install Dependencies

> Install utilities and RabbitMQ

- Open an admin powershell to `<repo-root>`.
- Install dependency packages:
  ```bash
  pdm run setup-win install.broker-deps
  ```

### Open Required Ports

> Open the relevant ports up so worker and client nodes can connect to the
> broker.

!!! Note
    If you only intend to use the broker with workers and clients on the same
    machine then you don't need to open ports.

#### **Option 1:** Open only `<broker-port>`. (Default: 5672)

The instructions for this are too configuration specific for us to provide.

#### **Option 2:** Disable broker firewalls entirely.

We can't provide general instructions for this step but if you're using
Windows Server 2019 you can use one of our scripts.

!!! warning
    This is not secure at all. Do not do this if the license
    server is at all accessible from public or untrusted computers.

- Disable the Windows Server 2019 firewall:
  ```bash
  pdm run setup-win license-server.disable-firewall
  ```

**Note:** This might work with other versions of Windows but that hasn't been
tested.

### Preserve Settings

- Keep this machine's IP as: `<broker-ip>`
- Keep rabbitmq's open port as: `<broker-port>` (default: 5672)

### Start RabbitMQ Service

- Start the RabbitMQ service:
    - Start Menu -> RabbitMQ Server -> RabbitMQ Service Start

The server should automatically start on boot.
