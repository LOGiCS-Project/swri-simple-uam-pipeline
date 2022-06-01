# AWS Service Setup

Instructions for setting up your AWS shared services if you're trying to use
AWS for other nodes in this system.

**Note:** Things in angle brackets `<like-this>` are placeholders to be filled in
by the user.

## Elastic IP

Provides a public IP for the private cloud you're setting up.

  - Allocate Elastic IP:
    - https://console.aws.amazon.com/vpc/home?region=us-east-1#Addresses:
    - Save to: `<aws-elastic-ip>`

## Virtual Private Cloud

Creates public and private subnets that your servers can live in.

  - Use Wizard to Create VPC `<aws-vpc>` w/ Public and Private Subnets
    - https://console.aws.amazon.com/vpc/home?region=us-east-1#wizardSelector
    - IPv4 CIDR : 10.0.0.0/16
    - IPv6 CIDR : None
    - VPC Name : `<aws-vpc>`
    - Public Subnet:
      - IPv4 CIDR : 10.0.10.0/16
      - Availability Zone : No Pref
      - Name : `<aws-public-subnet>`
    - Private Subnet:
      - IPv4 CIDR : 10.0.20.0/16
      - Availability Zone : No Pref
      - Name : `<aws-private-subnet>`
    - Elastic IP: `<aws-elastic-ip>`
    - Service Endpoints: None
    - Enable DNS Hostnames: Yes
    - Hardware Tenancy: Default
    - Enable ClassicLink: No

  - Also change SGs to allow all connections w/in the Subnet
    - Add an inbound rule for all traffic on 10.0.0.0/8 on the default Security
      group.

## AWS VPN Connection

Sets up keys and a VPN connection so your local computer can directly
communicate with instances and services on the private subnet.

  - Create keys for VPN access
    - Create sever and client certs:
      - https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/client-authentication.html#mutual
      - Save as: `<aws-keypair>`,`<aws-server-cert>`, and `<aws-client-cert>`
    - Import the certs to ACM:
      - https://docs.aws.amazon.com/acm/latest/userguide/import-certificate-api-cli.html


  - Create VPN
    - https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-getting-started.html
    - Step 2:
      - name: SWRI-H1-VPN
      - Client IPV4 CIDR: 10.10.0.0/22
      - Server Cert ARN: `<aws-server-cert>`
      - Authentication Option: Mutual
      - Client Cert ARN: `<aws-client-cert>`
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
      - VPC : `<aws-vpc>`
      - Subnet : `<aws-private-subnet>`
    - Step 4:
      - Add Auth Rule:
        - Dest Network: 10.0.0.0/16
        - Grant Access: all users
    - Step 5:
      - Route dest: 0.0.0.0/0
      - target subnet: `<aws-private-subnet>`
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
      - VPC: `<aws-vpc>`
      - Subnet: `<aws-private-subnet>`
    - Save FSx IP as: `<aws-fsx-ip>`

  - Set permissions to maximally open:
    - From FSx control panel open up the newly created volume.
    - Actions -> Update Volume
    - **NFS Exports:**
      - **Client Address:** *
      - **NFS Options:** rw,no_auth_nlm,all_squash,anonuid=0,anongid=0,crossmnt
    - This will give all users root access to the drive and is horrible insecure
      but very convenient if you're using the drive to bridge between a local
      machine and a cloud VM.
      - Under no circumstances should you use these options if the interface
        is accessible from the public internet.

  - Attach Fsx ON Linux (change IP to appropriate for new FSx interface)
    - Get IP for FSx via network interface
      - IP: `<aws-fsx-ip>`
    - `sudo apt-get -y install nfs-common`
    - `mkdir fsx`
    - `sudo mount -t nfs -o nfsvers=4.1 <aws-fsx-ip>:/fsx/ fsx`
    - Consider using nfs caching and async. (google for details)

  - Attach on Windows (change IP to new FSx interface)
    - Open `cmd.exe` as admin (Not powershell)
    - `mount \\<aws-fsx-ip>\fsx\ Z:`
    - Data will now be attached to Z:
