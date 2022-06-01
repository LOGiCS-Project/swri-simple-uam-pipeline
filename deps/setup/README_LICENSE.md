# Windows License Server Setup

AWS only and shared setup for the license server.

If you are running the license server on a worker node then follow the
instructions [here](README_WORKER.md), which will prompt you to come back
to this document when appropriate.

**Note:** Things in angle brackets `<like-this>` are placeholders to be filled in
by the user.

## AWS Instance Setup

Make sure you've followed the instructions [here](README_AWS.md) first.
Fields created in that section will be prefixed with 'aws', e.g. `<aws-keypair>`.

### Provision License Server (AWS)

Create a new instance in the AWS Console with the following **minimum** settings:

  - **Name:** `<instance-name>`
  - **Application and OS Images:** Quick Start -> Windows
    - Microsoft Windows Server 2019 Base
  - **Instance Type:** t1.micro
    - 1x vCPU
    - 0.6gb Memory
  - **Key Pair:** `<aws-keypair>`
  - **Network Settings:**
    - **VPC:** `<aws-vpc>`
    - **Subnet:** `<aws-private-subnet>`
    - **Auto-assign Public IP:** Disable
    - **Firewall:** Select existing security group
      - **Common Security Groups:** `<aws-security-group>`
    - **Advanced Network Configuration:** None
  - **Configure Storage:** 1x 30gb gp2

### Connect to License Server (AWS)

Get license server connection information

 - Select the instance on your EC2 Dashboard
 - Hit the Connect Button
 - Connect to Instance -> RDP Client
 - Keep note of:
   - **Private IP:** `<license-server-ip>`
   - **Username:** `<license-server-user>`
   - **RDP File:**
     - Click "Download remote desktop file"
     - Save to `<license-server-rdp-file>`
   - **Password:**
     - Click "Get Password"
     - Upload `<aws-keypair>`.pem
     - Click "Decrypt Password"
     - Save to `<license-server-rdp-pass>`

Connect to license-server:

  - Via Preferred RDP client (e.g. Remmina):
    - **Import:** `<license-server-rdp-file>`
    - **IP:** `<license-server-ip>`
    - **Username:** `<license-server-user>`
    - **Password:** `<license-server-rdp-pass>`

### Initial License-Server Setup (AWS)

AWS specific license-server setup.

  - Add/Remove Features:
    - Add NFS client: https://computingforgeeks.com/install-and-configure-nfs-client-on-windows-10-server-2019/
  - Setup The Automount of drive:
    - https://docs.aws.amazon.com/fsx/latest/WindowsGuide/using-file-shares.html#map-share-windows
    - Open Map Network Drive:
      - Drive: D:
      - Folder: `\\<aws-fsx-ip>\fsx\`
      - Reconnect At Login: Yes

## License Server Setup

General setup for all license servers.

### Install Chocolatey and Minimal Deps

This downloads a minimal install script for chocolatey, git, python, and
miniconda3.
This step is idempotent and will just do nothing if these are all installed.

  - Open admin powershell and run:
    - `iwr -Uri https://raw.githubusercontent.com/LOGiCS-Project/swri-simple-uam-pipeline/main/setup/data/bootstrap_win.ps1 | iex`
  - Close this powershell terminal and open new ones for future steps.

### Get This Repo

Get this repo onto the machine somehow, cloning is the default method.
If you have a shared drive, placing the repo there will allow local development
without constant pushing and pulling.

  - **Option 1:** Clone from Github (HTTP):
    - `git clone https://github.com/LOGiCS-Project/swri-simple-uam-pipeline.git`
  - **Option 2:** Clone from Github (SSH):
    - `git clone git@github.com:LOGiCS-Project/swri-simple-uam-pipeline.git`

From here `<repo-root>` will refer to the repo's location.

### Setup Conda Env

Setup the conda env for this repo.

  - Update the base conda env:
    - Open: Start Menu -> Anaconda 3 -> Anaconda Powershell Prompt (right-click run as admin)
    - Run: `conda update -n base -c defaults conda`
  - Create the project env:
    - Navigate to `<repo-root>`
    - Run: `conda env create -f environment.yml`

For all future steps use an admin powershell with the conda env running.

  - Enter the conda env:
    - Open: Start Menu -> Anaconda 3 -> Anaconda Powershell Prompt (right-click run as admin)
    - Run: `conda activate simple-uam`

### Initialize Setup Package

Initalize pdm and packages for worker setup.

  - Open admin conda env at `<repo_root>\setup`
  - Setup sub-package pdm environment:
    - Run: `invoke setup`
    - **Or** run: `pdm install -d`
  - Test whether setup script was installed:
    - Run: `pdm run setup --help`
  - Reboot server

### Install Flexnet License Sever

Downloads and installs Flexnet Server.

  - Open admin conda env at `<repo_root>\setup`
  - Have your license information ready:
    - Get your mac address (for generating licenses):
      - Run: `pdm run setup mac-address`
    - Have the server license file for the above mac address downloaded
      somewhere convenient.
  - Run: `pdm run setup license-server.flexnet`
  - Read instructions in terminal and hit enter when ready.
  - Follow installer prompts until done.

Open the relevant ports up so workers can connect:

> **Note:** If you only intend to use Creo locally with a license server
> then you don't need to open ports up.

  - Open up port 7788 (or whatever port the server is configured to use).
    - Instructions will likely be setup specific.
  - **(Optional)** If on Windows Server 2019 you can disable the firewall completely.
    - **IMPORTANT:** This is not secure at all. Do not do this if the license
      server is at all accessible from public or untrusted computers.
    - Run: `pdm run setup license-server.disable-firewall`

Set up server:

  - Open: Start Menu -> PTC -> Flexnet Admin Web Interface
    - Open the administration page:
      - **Default User:** admin
      - **Default Pass:** admin
    - Change the password:
      - **Old Pass:** admin
      - **New Pass:** `<flexnet-password>`
    - Click: Administration -> Server Configuration -> Start Server

The server should automatically start on boot.
