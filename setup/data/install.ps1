# Sets up chocolately and downloads a number of packages for the machine. 
# Code copied from: https://stackoverflow.com/a/65068438

# Run this script in an admin powershell with packages as arguments.

## Install Each Individual Package ##

ForEach ($PackageName in $args)
{
   echo "Installing Chocolatey Package: $PackageName" 
   choco upgrade $PackageName -y
}