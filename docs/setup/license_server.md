# Creo License Server Setup

This sets up a floating Creo license that worker nodes can use.
A machine or VM with direct access can use a node-locked Creo license instead.
However if you need to access the VM through RDP a floating license is required.

Keep note of the IP of this machine as: `<license-server-ip>`

Ensure you've completed the steps in [General Setup](general.md) already.

### Get License File

Get the host-id and license file.

- Open an admin powershell to `<repo-root>`:
    - Run: `pdm run setup-win mac-address`
    - The result is the `<host-id>` for your license.
- Get the Creo floating license for `<host-id>`.
    - Place the license file somewhere accessible on the machine.

### Install Dependencies

Install utilities like wget and rsync.

- Open an admin powershell to `<repo-root>`:
    - Run: `pdm run setup-win install.license-deps`

### Install Flexnet Server

Install license server software.

- Open an admin powershell to `<repo-root>`:
    - Run: `pdm run setup-win license-server.flexnet`
- Wait for installer to download and hit enter when prompted.
- Follow install prompts until done.

### Open Required Ports

!!! Note
    If you only intend to use Creo locally with a license server
    then you don't need to open ports up.

Open the relevant ports up so workers can connect:

- Open up port 7788 (or whatever port the server is configured to use).
    - Instructions will likely be setup specific.
- **(Optional)** If on Windows Server 2019 you can disable the firewall completely.

    !!! warning
        This is not secure at all. Do not do this if the license
        server is at all accessible from public or untrusted computers.

        Run: `pdm run setup-win license-server.disable-firewall`

### Configure Server

- Open: Start Menu -> PTC -> Flexnet Admin Web Interface
    - Open the administration page:
        - **Default User:** admin
        - **Default Pass:** admin
    - Change the password:
        - **Old Pass:** admin
        - **New Pass:** `<flexnet-password>`
    - Click: Administration -> Server Configuration -> Start Server

The server should automatically start on boot.
