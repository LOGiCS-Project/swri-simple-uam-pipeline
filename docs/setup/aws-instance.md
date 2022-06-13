# Amazon Web Services (AWS) Instance Setup

This section of the guide will cover:

  - Creating the various EC2 instances needed for each node or combination of
    nodes.

## Provisioning an Instance

Setup an EC2 instance for running various nodes.
This only covers the various windows nodes that SimpleUAM currently supports
and needs to be repeated for each node.

- Under the EC2 Console click "Launch an Instance".

    ??? note "Creo License Server Minimum Requirements"

        The license server is simple enough we only need a free tier windows
        instance.

        - **Name:** `<instance.name>`
        - **Application and OS Images:** Quick Start -> Windows
            - Microsoft Windows Server 2019 Base
        - **Instance Type:** t1.micro
            - 1x vCPU
            - 0.6gb Memory
        - **Key Pair:** `<ec2-keypair>`
        - **Network Settings:**
            - **VPC:** `<aws-vpc>`
            - **Subnet:** `<aws-private-subnet>`
            - **Auto-assign Public IP:** Disable
            - **Firewall:** Select existing security group
            - **Common Security Groups:** `<aws-security-group>`
            - **Advanced Network Configuration:** None
        - **Configure Storage:** 1x 30gb gp2

    ??? note "Worker Node Minimum Requirements"

        The worker node needs an elastic graphics interface for Creo's UI to
        work.

        - **Name:** `<instance.name>`
        - **Application and OS Images:** Quick Start -> Windows
            - Microsoft Windows Server 2019 Base
        - **Instance Type:** t2.large
            - 2x vCPU
            - 8gb Memory
        - **Key Pair:** `<ec2-keypair>`
        - **Network Settings:**
            - **VPC:** `<aws-vpc>`
            - **Subnet:** `<aws-private-subnet>`
            - **Auto-assign Public IP:** Disable
            - **Firewall:** Select existing security group
            - **Common Security Groups:** `<aws-security-group>`
            - **Advanced Network Configuration:** None
        - **Configure Storage:** 1x 1000gb gp2
        - **Advanced Details:**
            - **Elastic GPU:** eg1.medium

    ??? note "Corpus Server Minimum Requirements"

        The corpus server provided with SimpleUAM is a minimal stub that
        can run on a worker node alongside a worker.

        A proper corpus server should probably be run on a linux instance
        in this VPC but setting that up is beyond the current scope of
        this library.

        If you must run the stub server is a persistant manner, then the
        worker node minimum requirements are a decent starting point. Maybe
        bump up the CPU a bit since it does tend to get saturated when the
        stub is being queried a lot.

    ??? note "Message Broker Minimum Requirements"

        We haven't tested the message broker enough to have good minimum
        requirements, but it can ride sidecar with a worker node.

        That said running a broker on windows for more than development work is
        not a great idea.
        Both supported brokers, rabbitmq and redis, are used out of the box
        with default settings.
        They both have much stronger linux support than windows support and
        they'll be more performant when running on an OS that's actually good.

        If you're running a broker in production just stick
        [rabbitmq](https://www.rabbitmq.com/download.html) or
        [redis](https://redis.io/download/) on linux instance.

- Find the instance you just created with "Name" `<instance.name>`.
    - Save the "Instance ID" as: `<instance.id>`

## Connect to an Instance

Get remote desktop connection information for the instance.

- Select the instance on your EC2 Dashboard
- Hit the Connect Button
- Connect to Instance -> RDP Client
- Keep note of:
    - **Private IP:** `<instance.ip>`
    - **Username:** `<instance.user>`
    - **RDP File:**
        - Click "Download remote desktop file"
        - Save to `<instance.rdp-file>`
    - **Password:**
        - Click "Get Password"
        - Upload `<ec2-keypair-pem>`
        - Click "Decrypt Password"
        - Save to `<instance.rdp-pass>`

Connect to the instance via rdp:

- Via Preferred RDP client (e.g. [Remmina](htps://remmina.org)):
    - **Import:** `<instance.rdp-file>`
    - **IP:** `<instance.ip>`
    - **Username:** `<instance.user>`
    - **Password:** `<instance.rdp-pass>`

## Mount Shared FSx Drive

AWS specific instance setup.

- Add NFS client: [Instructions](https://computingforgeeks.com/install-and-configure-nfs-client-on-windows-10-server-2019/)
- Setup The Automount of drive: [Instructions](https://docs.aws.amazon.com/fsx/latest/WindowsGuide/using-file-shares.html#map-share-windows)
    - Open File Explorer and click "Network" and "Map Network Drive":
      - **Drive**: `<fsx-drive-letter>`
      - **Folder**: `\\<aws-fsx-ip>\fsx\`
      - **Reconnect At Login**: Yes

**Continue to [General Setup](general.md)...**
