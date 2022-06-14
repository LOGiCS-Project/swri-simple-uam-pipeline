# Message Broker Setup

A message broker allows worker nodes to pull analysis requests from a shared
queue.
The standard message broker is [RabbitMQ](https://www.rabbitmq.com/) with
the default settings.

## **Option 1:** Run RabbitMQ on a Linux Machine *(Recommended)*

RabbitMQ is a backendless message broker that's sufficient if you're okay
with clients not being notified when the analysis result
is complete. (It will just appear in the results directory.)

- Follow the instructions [here](https://www.rabbitmq.com/download.html) to
  set up RabbitMQ.
    - Keep this machine's IP as: `<broker-ip>`
    - Keep rabbitmq's open port as: `<broker-port>` (default: 5672)

## **Option 2:** Run Redis on a Linux Machine

Redis can be configured as a response backend as well as a message broker.
This means that clients can get notified when an analysis is complete.

We have not tried to get this running so don't have install instructions.

## **Option 3:** Run RabbitMQ as a Windows Service

### Prerequisites

- [General Setup](general.md) has been completed.

### Install Dependencies

Install utilities and rabbitmq.

- Open an admin powershell to `<repo-root>`:
    - Run: `pdm run setup-win install.broker-deps`

### Open Required Ports

!!! Note
    If you only intend to use rabbitmq with local workers and clients.
    then you don't need to open ports up.

Open the relevant ports up so workers can connect:

- Open up port `<broker-port>` (default: 5672).
    - Instructions will likely be setup specific.
- **(Optional)** If on Windows Server 2019 you can disable the firewall completely.

    !!! warning
        This is not secure at all. Do not do this if the license
        server is at all accessible from public or untrusted computers.

        Run: `pdm run setup-win license-server.disable-firewall`

### Preserve Settings

- Keep this machine's IP as: `<broker-ip>`
- Keep rabbitmq's open port as: `<broker-port>` (default: 5672)

### Start RabbitMQ Service

- Click: Start Menu -> RabbitMQ Server -> RabbitMQ Service Start

The server should automatically start on boot.
