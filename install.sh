#!/bin/bash

# Check if the script is being run as root
if [ "$(id -u)" -eq 0 ]; then
    echo "Script must not be ran as root" >&2
    exit 1
fi

echo "FastFLX1 is an easy way to add some cool workarounds and features to your FLX1 device"

# Update system
sudo apt update
sudo apt upgrade -y --allow-downgrades
sudo apt update
sudo apt upgrade -y --allow-downgrades
sudo apt update
sudo apt upgrade -y --allow-downgrades

# Install required packages
sudo apt install wtype yad 

# Create necessary directories
mkdir -p "${HOME}/.config/autostart/"
mkdir -p "${HOME}/.local/share/applications/"
sudo mkdir -p /opt/fastflx1/
sudo mkdir -p /opt/fastflx1/scripts
sudo mkdir -p /opt/fastflx1/configs
sudo mkdir -p /opt/fastflx1/files

# Create symbolic links for the scripts and directories
sudo ln -s "${PWD}/" "/opt/fastflx1/"
sudo ln -s "${PWD}/scripts/" "/opt/fastflx1/scripts"
sudo ln -s "${PWD}/configs/" "/opt/fastflx1/configs"
sudo ln -s "${PWD}/files/" "/opt/fastflx1/files"
sudo ln -s "${PWD}/install.sh" "/opt/fastflx1/"
sudo ln -s "${PWD}/uninstall.sh" "/opt/fastflx1/"
sudo ln -s "${PWD}/update.sh" "/opt/fastflx1/"
sudo ln -s "${PWD}/README.md" "/opt/fastflx1/"

# Ensure the scripts are executable (for uninstall, update)
chmod +x "${PWD}/uninstall.sh"
chmod +x "${PWD}/update.sh"

# Apply chmod +x for all scripts in the "scripts" folder
for script in "${PWD}/scripts"/*; do
    if [ -f "$script" ]; then
        chmod +x "$script"
    fi
done

# If the scripts are symlinked, you need to apply chmod on the symlink target, not just the source
chmod +x "/opt/fastflx1/uninstall.sh"
chmod +x "/opt/fastflx1/update.sh"

# Apply chmod +x to all symlinked scripts in /opt/fastflx1/scripts
for script in "/opt/fastflx1/scripts"/*; do
    if [ -f "$script" ]; then
        chmod +x "$script"
    fi
done

# Create desktop entries
ln -s "${PWD}/files/fastflx1.desktop" "${HOME}/.local/share/applications/fastflx1.desktop"
ln -s "${PWD}/configs/alarmvol.desktop" "${HOME}/.config/autostart/alarmvol.desktop"
ln -s "${PWD}/configs/dialtone.desktop" "${HOME}/.config/autostart/dialtone.desktop"

# Add FastFLX1 paths to the system's PATH
echo 'export PATH=$PATH:/opt/fastflx1' >> ~/.bashrc
echo 'export PATH=$PATH:/opt/fastflx1/scripts' >> ~/.bashrc

# Reload bashrc to apply changes
source ~/.bashrc

echo "FastFLX1 setup complete"
