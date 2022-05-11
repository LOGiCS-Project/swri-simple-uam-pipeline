# AWS Service Setup

Instructions for setting up your AWS shared services if you're trying to use
AWS for other nodes in this system.

## Elastic IP

Provides a public IP for the private cloud you're setting up.

  - Allocate Elastic IP:
    - https://console.aws.amazon.com/vpc/home?region=us-east-1#Addresses:

## Virtual Private Cloud

Creates public and private subnets that your servers can live in.

  - Use Wizard to Create VPC w/ Public and Private Subnets
    - https://console.aws.amazon.com/vpc/home?region=us-east-1#wizardSelector
    - IPv4 CIDR : 10.0.0.0/16
    - IPv6 CIDR : None
    - VPC Name : SWRI-H1-VPC
    - Public Subnet:
      - IPv4 CIDR : 10.0.10.0/16
      - Availability Zone : No Pref
      - Name : Public Subnet
    - Private Subnet:
      - IPv4 CIDR : 10.0.20.0/16
      - Availability Zone : No Pref
      - Name : Private Subnet
    - Elastic IP: Use previously allocated EIP
    - Service Endpoints: None
    - Enable DNS Hostnames: Yes
    - Hardware Tenancy: Default
    - Enable ClassicLink: No

  - Also need to change SGs to allow all connections w/in the Subnet
    - Add an inbound rule for all traffic on 10.0.0.0/8 on the default Security
      group.

## AWS VPN Connection

Sets up keys and a VPN connection so your local computer can directly
communicate with instances and services on the private subnet.

  - Create keys for VPN access
    - Create sever and client certs:
      - https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/client-authentication.html#mutual
    - Import the certs to ACM:
      - https://docs.aws.amazon.com/acm/latest/userguide/import-certificate-api-cli.html
      - once for server
      - once for clien
      - use ca.crt as the keychain

  - Create VPN
    - https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-getting-started.html
    - Step 2:
      - name: SWRI-H1-VPN
      - Client IPV4 CIDR: 10.10.0.0/22
      - Server Cert ARN; (From previous step)
      - Authentication Option: Mutual
      - Client Cert ARN: (from previous step)
      - Log client Details?: No
      - Enable client Connect: no
      - Optional Params:
        - Transport: UDP
        - Enable Split Tunnel: Yes
        - VPC ID: (Use created VPC from earlier)
        - VPN Port: 443
        - Enable Self-Service : yes
        - Session Timeout: 24h
        - Enable Client Logic Banner: No
    - Step 3: Client VPN Assoc
      - VPC : As created
      - Subnet : Private Subnet
    - Step 4:
      - Add Auth Rule:
        - Dest Network: 10.0.0.0/16
        - Grant Access: all users
    - Step 5:
      - Route dest: 0.0.0.0/0
      - target subnet: Private Subnet
    - Step 6: As stated
    - Step 7: Connect to VPN
      - https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-getting-started.html

## FSx Shared Drive

Create a shared drive that you can mount on both your local machine and worker
nodes.
Don't use git to push changes to a worker during development, it's not fast
enough to iterate with, put your code on the shared drive.
(Production is different, since you won't be changing the code rapidly and
you generally want to only have more stable code running.)

  - Create an FSx File System:
    - https://console.aws.amazon.com/fsx/home?region=us-east-1#file-systems
    - Create File System:
      - Type: Quick Create
      - Name: Shared-Store
      - Capacity: 100gb
      - VPC: (Our base VPC)
      - Subnet: (Private Subnet)

  - Attach Fsx ON Linux (change IP to appropriate for new FSx interface)
    - Get IP for FSx via network interface
      - IP: 10.0.20.223
    - `sudo apt-get -y install nfs-common`
    - `mkdir fsx`
    - `sudo mount -t nfs -o nfsvers=4.1 10.0.20.223:/fsx/ fsx`
    - Consider using nfs caching and async. (google for details)

  - Attach on Windows (change IP to new FSx interface)
    - Open `cmd.exe` as admin (Not powershell)
    - `mount \\10.0.20.223\fsx\ Z:`
    - Data will now be attached to Z:
