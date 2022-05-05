# Windows License Server Setup

AWS only and shared setup for the license server.

## AWS Instance Setup (needs updating)

Make sure you've followed the instructions [here](README_AWS.md) first.

  - Provision Windows License Server:
    - New Instance:
      - Step 1:
        - AMI: Windows 2019 w/ Containers
      - Step 2:
        - Instance Type: t2.micro
      - Step 3:
        - Network: (previously created VPC)
        - Subnet: (Private subnet)
      - Step 4, 5: (Defaults)
      - Step 6: (Default security group)
        - The one w/ the all inbound traffic from 10.0.0.0/8 rule
      - Select Key Pair:
        - If there is an existing KP use that, otherwise create new and
          save it somewhere.
    - Start the instance.

  - Setup Windows License Server:
    - Get the RDP Login File and import into RDP client:
      - On the shared drive: `certs/Creo-License-Server.rdp`
      - Pass: 9M;sGdp!CF)3eja%?i3x;xAFf?*8Ss-j
      - RDP into the server
    - Add/Remove Features:
      - Add NFS client: https://computingforgeeks.com/install-and-configure-nfs-client-on-windows-10-server-2019/
    - Setup The Automount of drive:
      - https://docs.aws.amazon.com/fsx/latest/WindowsGuide/using-file-shares.html#map-share-windows
      - Open Map Network Drive:
        - Drive: D:
        - Folder: \\fs-04c9da0d5b7b8d9e3.fsx.us-east-1.amazonaws.com\fsx\
        - Reconnect At Login: Yes

## License Server Setup (needs updating)

Make sure you have access to this repo somewhere on the new machine.

  - Setup Chocolatey: (admin powershell)
    - `D:\src\chocolatey\setup.ps1`
    - `RefreshEnv.cmd`
  - Setup Python: (admin powershell)
    - `choco install python --version=3.10.0 -y`
    - Close shell
  - Install Utilities and QoL Apps:
    - Open new admin powershell
    - `cd D:`
    - `python -m setup_aws_worker --run utils qol`
  - Extract `D:data/flexnetadmin64_11/17/1/0` to a folder on desktop
    - run `setup.exe`
    - use lisence `lm_16274162_3208204`
    - open `PTC/Flexnet Web ADmin` from start menu
    - open adeministration page:
      - user: admin
      - pass: admin
    - change pass:
      - old pass: admin
      - new pass: password
    - click start flexnet admin to run server.
  - Go into windows network and security settings:
    - Turn off all the firewalls completely
