#!/bin/bash

if [ "$(id -u)" -eq 0 ]; then
    echo "Script must not be ran as root"
    exit 1
fi

echo "FastFLX1 is easy to way to add some cool workarounds and features to your FLX1 device"


sudo apt update
sudo apt upgrade --allow-downgrades
sudo apt update
sudo apt upgrade --allow-downgrades
sudo apt install wtype

mkdir -p "${HOME}/.config/autostart/"
mkdir -p "${HOME}/.local/share/applications/"
sudo mkdir -p /opt/fastflx1/scripts
sudo mkdir -p /opt/fastflx1/configs
sudo mkdir -p /opt/fastflx1/files
sudo ln -s "${PWD}/scripts/.sh" "/opt/fastflx1/scripts"
sudo ln -s "${PWD}/configs/gtk.css" "/opt/fastflx1/configs"
sudo ln -s "${PWD}/files/wallpaper.svg" "/opt/fastflx1/files"
## sudo ln -s "${PWD}/desktop/fastcontacts.desktop" "/opt/fastcalls/desktop" (just reminder)
sudo ln -s "${PWD}/install.sh" "/opt/fastflx1/"
sudo ln -s "${PWD}/uninstall.sh" "/opt/fastflx1/"
sudo ln -s "${PWD}/update.sh" "/opt/fastflx1/"
sudo ln -s "${PWD}/README.md" "/opt/fastflx1/"
## ln -s "${PWD}/desktop/fastcontacts.desktop" "${HOME}/.local/share/applications/fastcontacts.desktop" (reminder)
## ln -s "${PWD}/desktop/fasthistory.desktop" "${HOME}/.config/autostart/fasthistory.desktop" (reminder)
