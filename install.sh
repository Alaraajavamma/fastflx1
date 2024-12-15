#!/bin/bash

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
mkdir -p "${HOME}/.config/assistant-button/"
mkdir -p "${HOME}/.config/feedbackd/"
mkdir -p "${HOME}/.config/gtk-3.0/"
mkdir -p "${HOME}/.local/share/applications/"
mkdir -p "${HOME}/.local/share/sounds/__custom/"
mkdir -p "${HOME}/.local/share/squeekboard/keyboards/"
mkdir -p "${HOME}/.local/share/squeekboard/keyboards/email/"
mkdir -p "${HOME}/.local/share/squeekboard/keyboards/emoji/"
mkdir -p "${HOME}/.local/share/squeekboard/keyboards/number/"
mkdir -p "${HOME}/.local/share/squeekboard/keyboards/pin/"
mkdir -p "${HOME}/.local/share/squeekboard/keyboards/terminal/"
mkdir -p "${HOME}/.local/share/squeekboard/keyboards/url/"

# Ensure the scripts are executable
sudo chmod +x "${HOME}/.git/fastflx1/uninstall.sh"
sudo chmod +x "${HOME}/.git/fastflx1/update.sh"
sudo chmod +x "${HOME}/.git/fastflx1/scripts/*"

# Move config folders to the user's .config directory
# Make sure the target directory exists
cp -r HOME}/.git/fastflx1/configs/assistant-button/* ${HOME}/.config/assistant-button/
cp -r HOME}/.git/fastflx1/configs/autostart/* ${HOME}/.config/autostart/
cp -r HOME}/.git/fastflx1/configs/feedbackd/* ${HOME}/.config/feedbackd/
cp -r HOME}/.git/fastflx1/configs/gtk-3.0/* ${HOME}/.config/gtk-3.0/
cp -r HOME}/.git/fastflx1/share/squeekboard/* ${HOME}/.local/share/squeekboard/
cp -r HOME}/.git/fastflx1/share/sounds/* ${HOME}/.local/share/sounds/


# Create desktop entries
cp ${HOME}/.git/fastflx1/files/fastflx1.desktop ${HOME}/.local/share/applications/fastflx1.desktop
cp ${HOME}/.git/files/yad-icon-browser.desktop ${HOME}/.local/share/applications/yad-icon-browser.desktop
cp ${HOME}/.git/configs/alarmvol.desktop ${HOME}/.config/autostart/alarmvol.desktop
cp ${HOME}/.git/configs/dialtone.desktop ${HOME}/.config/autostart/dialtone.desktop

# Add FastFLX1 paths to the system's PATH
echo 'export PATH=$PATH:/home/furios/.git/fastflx' >> ~/.bashrc
echo 'export PATH=$PATH:/home/furios/.git/fastflx/.git' >> ~/.bashrc

# Reload bashrc to apply changes
source ~/.bashrc

gsettings set org.gnome.desktop.sound theme-name __custom

echo "FastFLX1 setup complete"