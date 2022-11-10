# Amazon Web Services (AWS) Network Setup

This section of the guide will cover:

  - Setting up a virtual private cloud (VPC) to contain SUAM nodes.
  - Creating a VPN connection into that cloud for home access.
  - Creating a shared network drive for hosting code and analysis results.

## Initial Steps {#initial}

Most operations will require access to the
[AWS Console](https://console.aws.amazon.com/) so ensure you have a valid amazon
AWS account.

!!! info

    This guide assumes that you have full access to AWS. In principle nothing
    should prevent an IAM user from performing all these steps except knowing
    the set of neccesary permissions.

    If you do use an IAM user for this install process, please tell us what
    policies you used so we can include them in this guide.

## Choose an Availability Zone {#az}

> AWS features clusters of cloud computing resources called
> [availability zones](https://docs.aws.amazon.com/AWSEC2/latest/WindowsGuide/using-regions-availability-zones.html#concepts-availability-zones) (AZs).
> Different features of AWS are available on each AZ so you should choose one
> with access to everything you intend to use.

!!! info

    This guide assumes that all actions are taking place within a single AZ, and
    that no bridges between zones are needed.

- Choose an AZ that supports all the features you intend to use.

    ??? abstract "AZ Availability Lists for AWS Services"

        Here are links to the AZ lists for a number of services you might want to use:

        - **[FSx for OpenZFS](https://docs.aws.amazon.com/fsx/latest/OpenZFSGuide/what-is-fsx.html)**: Used to provide a shared drive for workers and clients.
        - **Brokers:**
            - **[AmazonMQ](https://docs.aws.amazon.com/general/latest/gr/amazon-mq.html)**: RabbitMQ compatible broker service. *(Optional)*
            - **[MemoryDB for Redis](https://docs.aws.amazon.com/general/latest/gr/memorydb-service.html)**: Redis compatible broker service. *(Optional)*
            - **[ElastiCache for Redis](https://docs.aws.amazon.com/general/latest/gr/elasticache-service.html)**: Redis compatible broker service. *(Optional)*
        - **Graph Databases:**
            - **[Neptune](https://docs.aws.amazon.com/general/latest/gr/neptune.html)**: Amazon managed graph database. *(Optional)*

- Switch AZs using the region selector as shown [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#using-regions-availability-zones-describe).
- If you cannot find a single AZ with all the neccesary features then use multiple
  VPCs and [VPC Peering](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) to allow
  services on each VPC to access each other.

## Virtual Private Cloud {#vpc}

> This creates a private network where your servers can live isolated from the
> internet yet able to communicate with each other.

### Create public and private subnets {#vpc-subnets}

- Open the VPC console's [Create VPC page](https://console.aws.amazon.com/vpc/home#CreateVpc:).
    - VPC Settings:
        - **Resources to Create**: VPC and more
    - Name tag auto-generation:
        - **Auto-generate**: Yes (check box)
        - **Name**: `<aws-vpc.prefix>` (pick your own and save it)
        - **IPv4 CIDR block**: 10.0.0.0/16
        - **IPv6 CIDR block**: No IPv6 CIDR block
    - **Number of Availability Zones**: 1
    - **Number of Public Subnets**: 1
    - **Number of Private Subnets**: 1
    - Customize subnets CIDR blocks:
        - **Public subnet CIDR block**: 10.0.0.0/20
        - **Private subnet CIDR block**: 10.0.128.0/20
    - **NAT gateways**: in 1 AZ
    - **VPC endpoints**: None (unless you want S3 access)
    - DNS options:
        - **Enable DNS Hostnames**: Yes (check box)
        - **Enable DNS Resolution**: Yes (check box)

### Save useful information {#vpc-save}

- Click "Create VPC". Once the process bar is done click "View VPC".
    - Keep track of:
        - "VPC Name" as: `<aws-vpc.name>`
        - "VPC ID" as: `<aws-vpc.id>`
- Open the [Elastic IPs page](https://console.aws.amazon.com/vpc/home#Addresses) on the VPC console:
    - Find `<aws-vpc>`'s external IP address.
        - It should be named *"`<aws-vpc.prefix>`-eip-..."*.
        - Keep track of:
            - "Name" as: `<aws-elastic-ip.name>`
            - "Allocated IPv4 address" as: `<aws-elastic-ip.addr>`
            - "Allocation ID" as: `<aws-elastic-ip.id>`
- Open the [Subnets page](https://console.aws.amazon.com/vpc/home#subnets) on the VPC console.
    - Find `<aws-vpc>`'s public subnet.
        - It should be named *"`<aws-vpc.prefix>`-subnet-public1-..."*.
        - Keep track of:
            - "Name" as: `<aws-public-subnet.name>`
            - "Subnet ID" as: `<aws-public-subnet.id>`
    - Find `<aws-vpc>`'s private subnet.
        - It should be named *"`<aws-vpc.prefix>`-subnet-private1-..."*.
        - Keep track of:
            - "Name" as: `<aws-private-subnet.name>`
            - "Subnet ID" as: `<aws-private-subnet.id>`

### Open up the internal firewall {#vpc-firewall}

- Open the [Security Groups page](https://console.aws.amazon.com/vpc/home#SecurityGroups) of the VPC console.
    - Find the security group whose "VPC ID" is `<aws-vpc.id>`.
        - Keep track of:
            - "Name" as: `<aws-default-sg.name>` (Assign if needed)
            - "Security group ID" as: `<aws-default-sg.id>`
        - Select the SG, go to "Inbound Rules" on the bottom pane, and click "Edit
          Inbound Rules".
            - Click "Add Rule":
                - **Type**: Elastic Graphics
                - **Source**: `<aws-default-sg.id>`
            - Click "Add Rule":
                - **Type**: All TCP
                - **Source**: 10.0.0.0/8
            - Click "Add Rule":
                - **Type**: All UDP
                - **Source**: 10.0.0.0/8
            - Click "Save rules"

## AWS VPN Connection {#vpn}

> Sets up keys and a VPN connection so your local computer can directly
> communicate with instances and services on the private subnet.

### Create keys for VPN access {#vpn-keys}

- Create sever and client certs:
    - Follow the instructions [here](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/client-authentication.html#mutual).
    - Keep track of:
        - `ca.crt` as: `<aws-ca-certs.crt>`
        - `ca.key` as: `<aws-ca-certs.key>`
        - `server.crt` as: `<aws-server-cert.crt>`
        - `server.key` as: `<aws-server-cert.key>`
        - `client1.domain.tld.crt` as: `<aws-client-cert.crt>`
        - `client1.domain.tld.key` as: `<aws-client-cert.key>`
- Import the server and client certs using the [ACM console](https://console.aws.amazon.com/acm/home):
    - Follow the instructions [here](https://docs.aws.amazon.com/acm/latest/userguide/import-certificate-api-cli.html).
        - **Certificate Body**: Content of `<aws-*-cert.crt>` between
          `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----`,
          inclusive.
        - **Certificate Private Key**: Content of `<aws-*-cert.key>`
        - **Certificate Chain**: Content of `<aws-ca-cert.crt>`
- Open the AWS Certificate Manager's [List Certificates page](https://console.aws.amazon.com/acm/home#/certificates/list):
    - For the server cert, with domain name "server":
        - Keep track of "Identifier" as: `<aws-server-cert.id>`
        - Keep track of "ARN" as: `<aws-server-cert.arn>`
    - For the client cert, with domain name "client1.domain.tld":
        - Keep track of "Identifier" as: `<aws-client-cert.id>`
        - Keep track of "ARN" as: `<aws-client-cert.arn>`

### Create the VPN interface {#vpn-interface}

- Follow the instructions [here](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-getting-started.html).
    - Step 2:
        - **Name**: `<aws-cvpn>`
        - **Client IPV4 CIDR**: 10.10.0.0/22
        - **Server Cert ARN**: `<aws-server-cert.arn>`
        - **Authentication Option**: Mutual
        - **Client Cert ARN**: `<aws-client-cert.arn>`
        - **Connection Logging**: No
        - **Client Connect Handler**: no
        - Optional Params:
            - **Transport**: UDP
            - **Enable Split Tunnel**: Yes
            - **VPC ID**: `<aws-vpc.id>`
            - **Security Group IDs**: `<aws-default-sg.id>`
            - **VPN Port**: 443
            - **Enable Self-Service**: yes
            - **Session Timeout**: 24h
            - **Enable Client Logic Banner**: No
        - Save the Client VPN ID as `<aws-cvpn.id>`
    - Step 3: Client VPN Assoc
        - **VPC**: `<aws-vpc.id>`
        - **Subnet**: `<aws-private-subnet.id>`
    - Step 4:
        - Add Auth Rule:
            - **Dest Network**: 10.0.0.0/8
            - **Grant Access**: all users
    - Step 5:
        - Add Route:
            - **Route Dest**: 0.0.0.0/0
            - **Target Subnet**: `<aws-private-subnet.id>`
        - Add Auth Rule:
            - **Dest Network**: 0.0.0.0/0
            - **Grant Access**: all users
    - Step 6: No changes
    - Step 7: Skip this step
    - Step 8: Skip this step

### Create Client VPN Config File {#vpn-client-config}

> This is the file users will import in order to connect to the above
> VPN interface. Instructions taken from [here](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-getting-started.html#cvpn-getting-started-config)
> and [here](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-working-endpoint-export.html).

- Open the Amazon VPC console at https://console.aws.amazon.com/vpc/
- In the navigation pane, choose "Client VPN Endpoints".
- Choose `<aws-cvpn.id>` and click "Download Client Configuration".
    - Save this as `<aws-cvpn.config>`.
- Open `<aws-cvpn.config>` in a text editor.
    - Prepend a random subdomain to the ClientVPN DNS entry
        - The line should start with `remote cvpn-endpoint-`.
        - When finished it should begin `remote ****.cvpn-endpoint-` with the
          rest remaining the same and `****` replaced with some random
          string of your own.
    - After the line that begins `verb 3` insert the following:
      ```xml
      <ca>
      </ca>

      <cert>
      </cert>

      <key>
      </key>
      ```
    - Place the content of `<aws-ca-cert.crt>` between the `<ca>` tags.
        - It's fine if this is already populated in the downloaded `<aws-cvpn.config>`.
    - Place the certificate from `<aws-client-cert.crt>` between the
      `<cert>` tags.
        - The certificate is what's between `-----BEGIN CERTIFICATE-----` and
          `-----END CERTIFICATE-----`, inclusive.
    - Place the content of `<aws-client-cert.key>` between the `<key>` tags.
    - Save the modified file.

        ??? example "Sample `<aws-cvpn.config>` after above modifications."

            The actual contents of the certificates have been replaced with `...`.

            ```
            client
            dev tun
            proto udp
            remote asdf.cvpn-endpoint-0011abcabcabcabc1.prod.clientvpn.eu-west-2.amazonaws.com 443
            remote-random-hostname
            resolv-retry infinite
            nobind
            remote-cert-tls server
            cipher AES-256-GCM
            verb 3

            <ca>
            -----BEGIN CERTIFICATE-----
            ...
            -----END CERTIFICATE-----
            </ca>

            <cert>
            -----BEGIN CERTIFICATE-----
            ...
            -----END CERTIFICATE-----
            </cert>

            <key>
            -----BEGIN PRIVATE KEY-----
            ...
            -----END PRIVATE KEY-----
            </key>

            reneg-sec 0
            ```

- Distribute the `<aws-cvpn.config>` to your intended users.


### Connect to the VPN {#vpn-connect}

> These instructions apply to your users as well as long as you provide them
> access to the `<aws-cvpn.config>` file.

- **Linux:** [Instructions](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/linux.html)
- **MacOS:** [Instructions](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/macos.html)
- **Windows:** [Instructions](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/windows.html)

## Shared Drive {#drive}

> Create a shared drive that you can mount on both your local machine and worker nodes.
> This drive is both a convenient shared mount for development work, using your
> local setup to edit server code, and a place for multiple workers to stash
> results.

### Option 1: Use Amazon FSx for OpenZFS {#drive-fsx}

- Go to the [FSx File System console](https://console.aws.amazon.com/fsx/home#file-systems).
    - Click [Create File System](https://console.aws.amazon.com/fsx/home#file-system-create):
        - **Select file system type**: OpenZFS
        - **Creation Method**: Standard create
        - File System Details:
            - **File system name**: `<aws-fsx.name>`
            - **SSD Storage capacity**: more than 50gb
            - **Provisioned SSD IOPS**: Automatic
            - **Throughput Capacity**: Recommended
        - Network and Security:
            - **VPC**: `<aws-vpc.name>`
            - **VPC Security Groups**: `<vpc-default-sg.name>`
            - **Subnet**: `<aws-private-subnet.name>`
        - Encryption:
            - **Encryption Key**: aws/fsx (default)
        - Root Volume Configuration:
            - **Data compression type**: No Compression
            - NFS Exports:
                - **Client Address:** *
                - **NFS Options:** rw,no_auth_nlm,all_squash,anonuid=0,anongid=0,crossmnt
            - **Record Size**: Default
        - Click "Next" then "Create File System"
    - Open the [file systems page on the FSx console](https://console.aws.amazon.com/fsx/home#file-systems) and select `<aws-fsx.name>`:
        - Keep track of "File System ID" as: `<aws-fsx.id>`
        - Open "Network Interface" and save"IPv4 address" as: `<aws-fsx.ip>`

??? info "Unix Mount Instructions"

    Ensure you're connected to the VPN.

    Choose and create a mount directory at `<local-mount>`.

    Make sure you have nfs utilities installed. For ubuntu: `sudo apt-get -y install nfs-common`.

    Run: `sudo mount -t nfs -o nfsvers=4.1 <aws-fsx-ip>:/fsx/ <local-mount>`

    Consider using nfs caching and async. (google for details)

??? info "Windows Mount Instructions"

    Ensure you're connected to the VPN.

    Chose a `<drive-letter>` to be the mount point. (e.g. 'Z:')

    Open `cmd.exe` as admin (Not powershell)

    Run: `mount \\<aws-fsx-ip>\fsx\ <drive-letter>`

??? info "Using FSx Drives in Config Files"

    Paths to FSx drives on a Windows box, such as the worker, should be in
    [UNC Format](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dfsc/149a3039-98ce-491a-9268-2f5ddef08192)
    so that access to a particular resource isn't tied to any specific drive name.

    In addition, you should replace any Windows forward slashes in a path with
    UNIX backslashes.

    For example, if you have an FSx drive mounted at `D:\\` with a results
    storage directory at `D:\\results` then config files should instead use
    the path `//<fsx-drive-ip>/fsx/results`.

## Create an EC2 Keypair {#ec2-keypair}

> This keypair is needed to connect to various EC2 instances in the VPC.

#### Create a keypair for connecting to AWS instances. {#ec2-keypair-create}

- Open the EC2 console to the [Key pairs page](https://console.aws.amazon.com/ec2/v2/home#KeyPairs:) and click
  "[Create key pair](https://console.aws.amazon.com/ec2/v2/home#CreateKeyPair:)".
    - **Name**: `<ec2-keypair.name>`
    - **Key Pair Type**: RSA
    - **Private Key Format**: .pem
    - Click "Create Key Pair"
- When prompted save the *"`<ec2-keypair.name>`.pem"* file as: `<ec2-keypair.pem>`

**Continue to [AWS Instance Setup](aws-instance.md)...**
