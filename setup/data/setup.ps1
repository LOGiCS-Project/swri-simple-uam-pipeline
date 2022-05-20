# Sets up chocolately and downloads a number of packages for the machine. 
# Code copied from: https://stackoverflow.com/a/65068438

# Run this script in an admin powershell with the following cmd: 
#    powershell -executionpolicy bypass -File C:\Users\user\Desktop\setup_chocolatey.ps1
            
## Setup Chocolatey If Needed ##

If(Test-Path -Path "$env:ProgramData\Chocolatey") {
  echo "Chocolately Already Installed"
}
Else {
  echo "Installing Chocolately" 
  Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))      
}