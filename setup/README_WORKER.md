# Windows Worker Setup

AWS only and shared setup for the license server.

**Note:** Things in angle brackets <like-this> are placeholders to be filled in
by the user.

## AWS Instance Setup

Make sure you've followed the instructions [here](README_AWS.md) first.
Fields created in that section will be prefixed with 'aws', e.g. <aws-keypair>.

### Provision Worker (AWS)

Create a new instance in the AWS Console with the following settings:

  - **Name:** <instance-name>
  - **Application and OS Images:** Quick Start -> Windows
    - Microsoft Windows Server 2019 Base
  - **Instance Type:** t2.large
    - 2x vCPU
    - 8gb Memory
  - **Key Pair:** <aws-keypair>
  - **Network Settings:**
    - **VPC:** <aws-vpc>
    - **Subnet:** <aws-private-subnet>
    - **Auto-assign Public IP:** Disable
    - **Firewall:** Select existing security group
      - **Common Security Groups:** <aws-security-group>
    - **Advanced Network Configuration:** None
  - **Configure Storage:** 1x 50gb gp2
  - **Advanced details:**
    - **Elastic GPU:** eg1.medium

### Connect to Worker (AWS)

Get Worker connection information

 - Select the instance on your EC2 Dashboard
 - Hit the Connect Button
 - Connect to Instance -> RDP Client
 - Keep note of:
   - **Private IP:** <worker-ip>
   - **Username:** <worker-user>
   - **RDP File:**
     - Click "Download remote desktop file"
     - Save to <worker-rdp-file>
   - **Password:**
     - Click "Get Password"
     - Upload <aws-keypair>.pem
     - Click "Decrypt Password"
     - Save to <worker-rdp-pass>

Connect to worker:

  - Via Preferred RDP client (e.g. Remmina):
    - **Import:** <worker-rdp-file>
    - **IP:** <worker-ip>
    - **Username:** <worker-user>
    - **Password:** <worker-rdp-pass>

### Initial Worker Setup (AWS)

AWS specific worker setup.

  - Add/Remove Features:
    - Add NFS client: https://computingforgeeks.com/install-and-configure-nfs-client-on-windows-10-server-2019/
  - Setup The Automount of drive:
    - https://docs.aws.amazon.com/fsx/latest/WindowsGuide/using-file-shares.html#map-share-windows
    - Open Map Network Drive:
      - Drive: D:
      - Folder: \\<aws-fsx-ip>\fsx\
      - Reconnect At Login: Yes

## Worker Setup

General setup for all workers

### Install Chocolatey and Minimal Deps

This downloads a minimal install script for chocolatey, git, python, and
miniconda3.
This step is idempotent and will just do nothing if these are all installed.

  - Open admin powershell and run:
    - `iwr -Uri https://raw.githubusercontent.com/LOGiCS-Project/swri-simple-uam-pipeline/feature/initial-setup/setup/data/bootstrap_win.ps1 iex`
  - Close this powershell terminal and open new ones for future steps.

### Get This Repo

Get this repo onto the machine somehow, cloning is the default method.
If you have a shared drive, placing the repo there will allow local development
without constant pushing and pulling.

  - **Option 1:** Clone from Github (HTTP):
    - `git clone https://github.com/LOGiCS-Project/swri-simple-uam-pipeline.git`
  - **Option 2:** Clone from Github (SSH):
    - `git clone git@github.com:LOGiCS-Project/swri-simple-uam-pipeline.git`

From here <repo-root> will refer to the repo's location.

### Setup Conda Env

Setup the conda env for this repo.

  - Open admin powershell to <repo-root> and run:
    - `conda env create -f environment.yml`

For all future steps use an admin powershell with the conda env running.

  - Enter the conda env:
    - Open: Start Menu -> Anaconda 3 -> Anaconda Powershell Prompt (right-click run as admin)
    - `conda activate simple-uam`

# OLD

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
