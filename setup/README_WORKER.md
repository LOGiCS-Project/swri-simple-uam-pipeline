# Windows Worker Setup

AWS only and shared setup for the license server.

## AWS Instance Setup (needs updating)

Make sure you've followed the instructions [here](README_AWS.md) first.

  - Provision Windows Worker 1:
    - New Instance:
      - Step 1:
        - AMI: Windows 2019 w/ Containers
      - Step 2:
        - Instance Type: t2.xlarge
      - Step 3:
        - Network: (previously created VPC)
        - Subnet: (Private subnet)
        - Elastic Graphics: eg1.medium
      - Step 4: 100gb
      - Step 5: (Defaults)
      - Step 6: (Default security group)
        - The one w/ the all inbound traffic from 10.0.0.0/8 rule
      - Select Key Pair:
        - If there is an existing KP use that, otherwise create new and
          save it somewhere.
    - Start the instance.

 - Setup Windows Worker 1:
    - Get the RDP Login File and import into RDP client:
      - On the shared drive: `certs/Worker-1.rdp`
      - Pass: Z.yqtGyJESzPcPcdlg6;rROupf9cz*!p
      - RDP into the server
    - Add/Remove Features:
      - Add NFS client: https://computingforgeeks.com/install-and-configure-nfs-client-on-windows-10-server-2019/
    - Setup The Automount of drive:
      - https://docs.aws.amazon.com/fsx/latest/WindowsGuide/using-file-shares.html#map-share-windows
      - Open Map Network Drive:
        - Drive: D:
        - Folder: \\10.0.20.223\fsx\
        - Reconnect At Login: Yes

## Worker Setup (needs updating)

Make sure you have access to this repo somewhere on the new machine.

  - Setup Chocolatey: (admin powershell)
    - `D:\src\chocolatey\setup.ps1`
    - `RefreshEnv.cmd`
  - Setup Python: (admin powershell)
    - `choco install python --version=3.10.0 -y`
    - Close shell
  - Install Utilities, QoL, and Dependency Apps:
    - Open new admin powershell
    - `cd D:`
    - `python -m setup_aws_worker --run utils qol deps`
      - Get a sandwich, this step is slow and hand-free.
    - Reboot here
    - In admin powershell:
    - `Add-PoshGitToProfile -AllHosts`
    - double-click and run `D:/misc/ContextMenuAdminTess.reg` to setup
      file explorer ctxt menu option to open admin terminal
  - Install OpenMeta:
    - `cd D:`
    - `python -m setup_aws_worker --run openmeta`
    - follow prompts on gui installer
  - Install Python Packages:
    - `cd D:`
    - `python -m setup_aws_worker --run pip-pkgs openmeta-pip-pkgs`
  - Install Matlab Runtime:
    - `cd D:`
    - `python -m setup_aws_worker --run matlab`
    - follow prompt on gui installer
  - Install Creo:
    - `cd D:`
    - `python -m setup_aws_worker --run creo`
    - follow prompt on gui installer
    - Use `7788@10.0.20.142` as the license address. (Use IP of the license node)
    - turn off data collection
