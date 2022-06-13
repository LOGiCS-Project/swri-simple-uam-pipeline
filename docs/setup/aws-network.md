# Amazon Web Services (AWS) Network Setup

This section of the guide will cover:

  - Setting up a virtual private cloud (VPC) to contain SUAM nodes.
  - Creating a VPN connection into that cloud for home access.
  - Creating a shared network drive for hosting code and analysis results.

## Initial Steps

Most operations will require access to the
[AWS Console](https://console.aws.amazon.com/) so ensure you have a valid amazon
AWS account.

!!! info

    This guide assumes that you have full access to AWS. In principle nothing
    should prevent an IAM user from performing all these steps except knowing
    the set of neccesary permissions.

    If you do use an IAM user for this install process, please tell us what
    policies you used so we can include them in this guide.

<!-- ## Creating an Elastic IP Address -->

<!-- Provides a public IP for the private cloud you're setting up. -->

<!--   - Open the VPC console's [Elastic IP page](https://console.aws.amazon.com/vpc/home?region=us-east-1#Addresses:). -->
<!--     - Under "Allocate Elastic IP": -->
<!--       - **Network Borker Group**: Default -->
<!--       - **Public IPv4 Address Pool**: Amazon's Pool -->
<!--     - Click "Allocate": -->
<!--       - Keep track of the newly allocated IP as: `<aws-elastic-ip>` -->

## Virtual Private Cloud

Creates public and private subnets that your servers can live in.

- Open the VPC console's [Create VPC page](https://us-east-1.console.aws.amazon.com/vpc/home?region=us-east-1#CreateVpc:).
    - VPC Settings:
        - **Resources to Create**: VPC and more
    - Name tag auto-generation:
        - **Auto-generate**: Yes (check box)
        - **Name**: `<aws-vpc>` (pick your own and save it)
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

Locate and save useful information about the VPC.

- Click "Create VPC". Once the process bar is done click "View VPC".
    - Keep track of the VPC ID as: `<aws-vpc-id>`
- Open the "Elastic IPs" page on the VPC console:
    - Find `<aws-vpc>`'s external IP address.
        - It should be named *"`<aws-vpc>`-eip-..."*.
        - Keep track of the "Allocated IPv4 address" under `<aws-elastic-ip>`
- Open the "Subnets" page on the VPC console.
    - Find `<aws-vpc>`'s public subnet.
        - It should be named *"`<aws-vpc>`-subnet-public1-..."*.
        - Keep track of "Subnet ID" as: `<aws-public-subnet>`
    - Find `<aws-vpc>`'s private subnet.
        - It should be named *"`<aws-vpc>`-subnet-private1-..."*.
        - Keep track of "Subnet ID" as: `<aws-private-subnet>`

Open up the internal firewall rules for easier setup.

- Open the "Security Groups" page of the VPC console.
    - Find the subnet whose "VPC ID" is `<aws-vpc-id>`.
        - Keep track of "Security group ID" as: `<aws-default-sg>`
        - Select it, go to "Inbound Rules" on the bottom pane, and click "Edit
        Inbound Rules".
            - Click "Add Rule":
                - **Type**: Elastic Graphics
                - **Source**: `<aws-default-sg>`
            - Click "Add Rule":
                - **Type**: All TCP
                - **Source**: 10.0.0.0/8
            - Click "Save rules"

## AWS VPN Connection

Sets up keys and a VPN connection so your local computer can directly
communicate with instances and services on the private subnet.

Create keys for VPN access.

- Create sever and client certs:
    - Follow the instructions [here](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/client-authentication.html#mutual).
    - Keep track of:
        - `server.crt` as: `<aws-server-cert>`
        - `server.key` as: `<aws-server-key>`
        - `client1.domain.tld.crt` as: `<aws-client-cert>`
        - `client1.domain.tld.key` as: `<aws-client-key>`
- Import the certs to ACM:
    - Follow the instructions [here](https://docs.aws.amazon.com/acm/latest/userguide/import-certificate-api-cli.html).
- Open the AWS Certificate Manager's "List Certificates" page.
    - For the server cert:
        - Keep track of "Identifier" as: `<aws-server-cert-id>`
        - Keep track of "ARN" as: `<aws-server-cert-arn>`
    - For the client cert:
        - Keep track of "Identifier" as: `<aws-client-cert-id>`
        - Keep track of "ARN" as: `<aws-client-cert-arn>`

Create the VPN interface.

- Follow the instructions [here](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-getting-started.html).
    - Step 2:
        - **Name**: `<aws-vpn>`
        - **Client IPV4 CIDR**: 10.10.0.0/22
        - **Server Cert ARN**: `<aws-server-cert-arn>`
        - **Authentication Option**: Mutual
        - **Client Cert ARN**: `<aws-client-cert-arn>`
        - **Log client Details?**: No
        - **Enable client Connect**: no
        - Optional Params:
            - **Transport**: UDP
            - **Enable Split Tunnel**: Yes
            - **VPC ID**: `<aws-vpc-id>`
            - **VPN Port**: 443
            - **Enable Self-Service**: yes
            - **Session Timeout**: 24h
            - **Enable Client Logic Banner**: No
    - Step 3: Client VPN Assoc
        - **VPC**: `<aws-vpc-id>`
        - **Subnet**: `<aws-private-subnet>`
    - Step 4:
        - Add Auth Rule:
            - **Dest Network**: 10.0.0.0/20
            - **Grant Access**: all users
    - Step 5:
        - **Route Dest**: 0.0.0.0/0
        - **Target Subnet**: `<aws-private-subnet>`
    - Step 6: No changes
    - Step 7: No changes

## FSx Shared Drive

Create a shared drive that you can mount on both your local machine and worker nodes.
This drive is both a convenient shared mount for development work, using your
local setup to edit server code, and a place for multiple workers to stash
results.

- Go to the [FSx File System console](https://console.aws.amazon.com/fsx/home?region=us-east-1#file-systems).
    - Click "Create File System":
        - **Select file system type**: OpenZFS
        - **Creation Method**: Standard create
        - File System Details:
            - **File system name**: `<aws-fsx-name>`
            - **SSD Storage capacity**: more than 50gb
        - Network and Security:
            - **VPC**: `<aws-vpc-id>`
            - **VPC Security Groups**: `<vpc-default-sg>`
            - **Subnet**: `<aws-private-subnet>`
        - Root Volume Configuration:
            - **Data compression type**: none
            - NFS Exports:
                - **Client Address:** *
                - **NFS Options:** rw,no_auth_nlm,all_squash,anonuid=0,anongid=0,crossmnt
        - Click "Next" then "Create File System"
    - Open the "file systems" page on the FSx console and select `<aws-fsx-name>`:
        - Keep track of "File System ID" as: `<aws-fsx-id>`
        - Open its "Network Interface" and save its "IPv4 address" as: `<aws-fsx-ip>`

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

## Create an EC2 Keypair

Create a keypair for connecting to AWS instances.

- Open the EC2 console to the "Key pairs" page and click "Create key pair".
    - **Name**: `<ec2-keypair>`
    - **Key Pair Type**: RSA
    - **Private Key Format**: .pem
    - Click "Create Key Pair"
- When prompted save the *"`<ec2-keypair>`.pem"* file as: `<ec2-keypair-pem>`

**Continue to [AWS Instance Setup](aws-instance.md)...**
