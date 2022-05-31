# Run with : powershell -executionpolicy bypass -File .\bootstrap_win.ps1

If(Test-Path -Path "$env:ProgramData\Chocolatey") {
}
Else {
  # InstallChoco
  Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
}

choco upgrade git -y
choco upgrade python3 -y
choco upgrade openssl -y
RefreshEnv.cmd
python -m pip install pdm