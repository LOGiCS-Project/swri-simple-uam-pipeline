# Message Broker Setup

A message broker allows worker nodes to pull analysis requests from a shared
queue.
The standard message broker is [RabbitMQ](https://www.rabbitmq.com/) with
the default settings.

## **Option 1:** Run RabbitMQ on a Linux Machine *(Recommended)* {#rabbitmq-linux}

> RabbitMQ is a backendless message broker that's sufficient if you're okay
> with clients not being notified when the analysis result
> is complete. (It will just appear in the results directory.)

- Follow the instructions [here](https://www.rabbitmq.com/download.html) to
  set up RabbitMQ.

- Save this machine's IP as: `<broker.ip>`
- Save rabbitmq's open port as: `<broker.port>` (default: 5672)

## **Option 2:** Run Redis on a Linux Machine {#redis-linux}

> Redis can be configured as a response backend as well as a message broker.
> This means that clients can get notified when an analysis is complete.

We have not tried to get this running so don't have install instructions.

- Save this machine's IP as: `<broker.ip>` and `<backend.ip>`
- Save redis's open port as: `<broker.port>` and `<backend.port>` (default: 6379)
- Save the redis database you're using as: `<broker.db>` and `<backend.db>` (default: "/0")

## **Option 3:** Run RabbitMQ as a Windows Service {#rabbitmq-win}

> This runs RabbitMQ as a windows service and is fine for development or
> production setups.

### Prerequisites {#rabbitmq-win-rereqs}

- [General Setup](general.md) has been completed.

### Install Dependencies {#rabbitmq-win-deps}

> Install utilities and RabbitMQ

- Open an admin powershell to `<repo-root>`.
- Install dependency packages:
  ```bash
  pdm run setup-win install.broker-deps
  ```

### Open Required Ports {#rabbitmq-win-ports}

> Open the relevant ports up so worker and client nodes can connect to the
> broker.

!!! Note ""
    If you only intend to use the broker with workers and clients on the same
    machine then you don't need to open ports.

#### **Option 1:** Open only `<broker.port>`. (Default: 5672) {#rabbitmq-win-ports-single}

The instructions for this are too configuration specific for us to provide.

#### **Option 2:** Disable broker firewalls entirely. {#rabbitmq-win-ports-clobber}

We can't provide general instructions for this step but if you're using
Windows Server 2019 you can use one of our scripts.

!!! warning "Do not do this on public or untrusted machines"

- Disable the Windows Server 2019 firewall:
  ```bash
  pdm run setup-win disable-firewall
  ```

**Note:** This might work with other versions of Windows but that hasn't been
tested.

### Preserve Settings {#rabbitmq-win-settings}

- Keep this machine's IP as: `<broker.ip>`
- Keep rabbitmq's open port as: `<broker.port>` (default: 5672)

### Start RabbitMQ Service

- Start the RabbitMQ service:
    - Start Menu -> RabbitMQ Server -> RabbitMQ Service Start

The server should automatically start on boot.

## **Option 4:** Use AmazonMQ on AWS as a broker {#amazonmq}

> Amazon MQ seems fine for use with SimpleUAM, though we've only performed
> cursory testing.

### Prerequisites {#amazonmq-prereqs}

- An AWS VPC at `<aws-vpc>` with a private subnet at `<aws-private-subnet>`.

### Create the Amazon MQ Broker {#amazonmq-create}

- Go to the [Amazon MQ console](https://console.aws.amazon.com/amazon-mq/) on AWS.
- Click "Create brokers":
    - Step 1:
        - **Broker engine types:** RabbitMQ
    - Step 2:
        - **Select deployment mode:** Single Instance Broker
    - Step 3:
        - **Broker Name:** `<aws-broker.name>`
        - **Broker Instance Type:** mq.t3.micro (or bigger, though you probably won't need it)
        - RabbitMQ access:
            - **Username:** `<aws-broker.user>`
            - **Password:** `<aws-broker.pass>`
        - Additional Settings:
            - **Access Type:** Private Access
            - **VPC and Subnets:** Select Existing VPC
                - **VPC:** `<aws-vpc>`
                - **Subnet:** `<aws-private-subnet>`
            - **Security Groups:** Select Existing SG w/ `<aws-default-sg>`
    - Step 4:
        - Check settings
        - Click "Create Broker"
- Wait ~20 minutes for the broker to be created.

### Preserve Settings {#amazonmq-settings}

- Go to the [Amazon MQ console](https://console.aws.amazon.com/amazon-mq/) on AWS.
- Under "Brokers" find `<aws-broker.name>` and click.
    - Under "Connections" find "Endpoints".
    - Save the URL under "AMQP" as `<broker.url>`.
        - Example: `amqps://b-8f2b68ab-3d0f-4a64-a2bf-24418ebf52d5.mq.us-east-1.amazonaws.com:5671`

## **Option 5:** Use Amazon MemoryDB on AWS as a broker {#memorydb}

> Amazon MemoryDB seems fine for use with SimpleUAM, though we've only performed
> cursory testing.
>
> This should allow for more advanced features like return messages when compared to RabbitMQ based
> brokers.

### Prerequisites {#memorydb-prereqs}

- An AWS VPC at `<aws-vpc>` with a private subnet at `<aws-private-subnet>`.

### Create Amazon MemoryDB Broker {#memorydb-create}

- Go to the [MemoryDB dashboard](https://console.aws.amazon.com/memorydb/home#/dashboard?getStarted=expand).
- Click "[Create Cluster](https://console.aws.amazon.com/memorydb/home#/clusters/create)":
    - Step 1: Cluster Settings
        - Choose Cluster Creation Method:
            - **Configuration type**: Create new cluster
        - Cluster Info:
            - **Name**: `<aws-broker.name>`
        - Subnet Groups:
            - **Subnet Groups**: Create new subnet group
            - **Name**: `<aws-private-subnet.group.name>`
            - **VPC ID**: `<aws-vpc.id>`
            - **Selected Subnets**: `<aws-private-subnet.id>`
        - Cluster Settings:
            - **Node Type**: db.t4g.small or db.t4g.medium
                - Larger won't be useful unless you have 50+ worker nodes running simultaneously.
            - **Number of Shards**: 1
            - **Replicas per Shard**: 0
    - Step 2: Advanced Settings
        - Security:
            - **Selected Security Groups**: `<aws-default-sg.id>`
            - **Encryption Key**: Default key
            - **Encryption in transit**: No encryption
    - Click "Create"
- Go to the [MemoryDB Clusters List](https://console.aws.amazon.com/memorydb/home#/clusters).
    - Click the entry for `<aws-broker.name>`.
    - Wait ~20m for the cluster to finish being created.
    - Save "Cluster endpoint" as: `<aws-broker.endpoint>`
    - Prepend "`redis://`" to `<aws-broker.endpoint>` and save as: `<broker.url>` and `<backend.url>`
        - This should look like "`redis://*.*.clustercfg.memorydb.*.amazonaws.com:6379`"
          with "`*`" taken as wildcards.
