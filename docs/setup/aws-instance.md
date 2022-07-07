# Amazon Web Services (AWS) Instance Setup

This section of the guide will cover:

  - Creating the various EC2 instances needed for each component or combination of
    component.

## Provisioning an Instance

> Setup an EC2 instance for running various components.
> This only covers the various windows nodes that SimpleUAM currently supports
> and needs to be repeated for each node.

- Under the EC2 Console click "Launch an Instance".

    ??? note "Creo License Server Minimum Requirements"

        The license server is simple enough we only need a free tier windows
        instance.

        - **Name:** `<instance.name>`
        - **Application and OS Images:** Quick Start -> Windows
            - Microsoft Windows Server 2019 Base
        - **Instance Type:** t2.micro
            - 1x vCPU
            - 1gb Memory
        - **Key Pair:** `<ec2-keypair.name>`
        - **Network Settings:**
            - **VPC:** `<aws-vpc.id>`
            - **Subnet:** `<aws-private-subnet.id>`
            - **Auto-assign Public IP:** Disable
            - **Firewall:** Select existing security group
            - **Common Security Groups:** `<aws-default-sg.id>`
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
        - **Key Pair:** `<ec2-keypair.name>`
        - **Network Settings:**
            - **VPC:** `<aws-vpc.id>`
            - **Subnet:** `<aws-private-subnet.id>`
            - **Auto-assign Public IP:** Disable
            - **Firewall:** Select existing security group
            - **Common Security Groups:** `<aws-default-sg.id>`
            - **Advanced Network Configuration:** None
        - **Configure Storage:** 1x 200gb gp2
        - **Advanced Details:**
            - **Elastic GPU:** eg1.medium

        This can get CPU bound, so it might make sense to bump it up.

    ??? note "Corpus DB Minimum Requirements"

        **Option 1:** If you need a read-only corpus DB itermittently for
        generating a static corpus, we reccomend just running the stub DB on a
        worker temporarily.

        **Option 2:** If you need a corpus DB for an alternate analysis
        pipeline and are fine with a non-persistent corpus then use a
        stub DB on a worker.

        **Option 3:** If you need a corpus that is persistent, shared between
        multiple workers, or needs to be performant then you should set up
        janus-graph on a linux machine.

        This is outside the scope of this guide and you should try to follow
        SWRI's instructions.

        **Option 4:** AWS's [Neptune DB](https://docs.aws.amazon.com/neptune)
        seems like a viable option, though the details are up to you to sort.

    ??? note "Message Broker Minimum Requirements"

        **Option 1:** If you want a non-backendless broker or one that's not
        wasting your money, set up a linux instance and skip to the section
        on [message broker setup](broker.md). I'm not sure what minimum
        requirements make sense.

        **Option 2:** If you want a backendless message broker for intermittent
        testing or development work then install it sidecar with a worker node.

        **Option 3:** If you want a backendless broker and are fine with lower
        performance the specifications for a worker node on a windows machine
        be fine.

        **Option 4:** An AmazonMQ node might work well, there are tentative
        instructions in the section on [message broker setup](broker.md).

        **Option 5:** An Amazon MemoryDB for Redis node might work well, there
        are tentative instructions in the section on [message broker setup](broker.md).

- Find the instance you just created with "Name" `<instance.name>`.
    - Save the "Instance ID" as: `<instance.id>`

## Connect to an Instance

> Use the remote desktop protocol to connect to the instance.

#### Get RDP Connection Information

- Select the instance on your EC2 Dashboard
- Hit the Connect Button
- Connect to Instance -> RDP Client
- Keep note of:
    - **Private IP:** `<instance.ip>`
    - **Username:** `<instance.user>`
    - **RDP File:**
        - Click "Download remote desktop file"
        - Save to `<instance.rdp.file>`
    - **Password:**
        - Click "Get Password"
        - Upload `<ec2-keypair.pem>`
        - Click "Decrypt Password"
        - Save to `<instance.rdp.pass>`

#### Connect Via RDP

- Make sure your local machine is connected to the VPN set up previously,
  otherwise none of the provided IPs will correctly resolve.
- Via Preferred RDP client (e.g. [Remmina](htps://remmina.org)):
    - **Import:** `<instance.rdp.file>`
    - **IP:** `<instance.ip>`
    - **Username:** `<instance.user>`
    - **Password:** `<instance.rdp.pass>`

## Mount Shared FSx Drive

> The AWS specific instructions are largely the same as the standard windows
> NFS ones, but they need certain server features to be enabled first.

- Add NFS client: [Instructions](https://computingforgeeks.com/install-and-configure-nfs-client-on-windows-10-server-2019/)
- Setup The Automount of drive: [Instructions](https://docs.aws.amazon.com/fsx/latest/WindowsGuide/using-file-shares.html#map-share-windows)
    - Open File Explorer and click "Network" and "Map Network Drive":
      - **Drive**: `<aws-fsx.drive-letter>` (e.g. "`D:`" or "`F:`")
      - **Folder**: `\\<aws-fsx.ip>\fsx\`
      - **Reconnect At Login**: Yes

**Continue to [General Setup](general.md)...**
