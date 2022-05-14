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
  - **Configure Storage:** 1x 100gb gp2
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
    - `iwr -Uri https://raw.githubusercontent.com/LOGiCS-Project/swri-simple-uam-pipeline/feature/initial-setup/setup/data/bootstrap_win.ps1 | iex`
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

  - Update the base conda env:
    - Open: Start Menu -> Anaconda 3 -> Anaconda Powershell Prompt (right-click run as admin)
    - Run: `conda update -n base -c defaults conda`
  - Create the project env:
    - Navigate to <repo-root>
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
    - Run: `pdm run worker-setup --list`
  - Reboot server

### Setup Chocolatey Packages

Uses Chocolatey to setup various dependencies and quality of life packages.

  - Open admin conda env at `<repo_root>\setup`
  - Install all packages:
    - Run: `pdm run worker-setup choco.install-all`
  - **Or** install only dependencies:
    - Run: `pdm run worker-setup choco.install-deps`
  - **(Optional)** Setup posh-git:
    - This will only add the posh-git prompt to a normal powershell session,
      installing it within a conda environment would require modifying the
      conda-hook script.
    - This requires that the quality of life packages are installed, which
      is normally part of running `choco.install-all` but can be done separately
      with: `pdm run worker-setup choco.install-qol`
    - Run: `pdm run worker-setup choco.activate-poshgit`

### Install Matlab Runtime

Downloads and installs the Matlab Runtime 2020b.

  - Open admin conda env at `<repo_root>\setup`
  - Run: `pdm run worker-setup install.matlab`
  - Read instructions in terminal and hit enter when ready.
  - Follow installer prompts until done.

### Install OpenMETA

Downloads and installs OpenMETA.

  - Open admin conda env at `<repo_root>\setup`
  - Run: `pdm run worker-setup install.openmeta`
  - Read instructions in terminal and hit enter when ready.
  - Follow installer prompts until done.

### Install Creo

Downloads and installs PTC Creo 5.6.

  - Open admin conda env at `<repo_root>\setup`
  - If using a local license file have it accessible on the target machine.
  - Run: `pdm run worker-setup install.creo`
  - Read instructions in terminal and hit enter when ready.
  - Follow installer prompts until done.
