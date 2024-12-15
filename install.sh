#!/bin/bash

if [ "$(id -u)" -eq 0 ]; then
    echo "Script must not be ran as root"
    exit 1
fi

sudo apt update
sudo apt upgrade -y
sudo apt update
sudo apt upgrade -y
sudo apt update
sudo apt upgrade -y
sudo apt install -y yad wtype 

sudo chmod +x "${HOME}/.git/fastflx1/uninstall.sh"
sudo chmod +x "${HOME}/.git/fastflx1/update.sh"

sudo cp "${HOME}/.git/fastflx1/scripts/*" "/usr/bin/"
sudo chmod +x /usr/bin/alarmvol
sudo chmod +x /usr/bin/dialtone
sudo chmod +x /usr/bin/double-press
sudo chmod +x /usr/bin/fastflx1
sudo chmod +x /usr/bin/gnome-weather-location
sudo chmod +x /usr/bin/long-press
sudo chmod +x /usr/bin/short-press
sudo chmod +x /usr/bin/squeekboard-scale

mkdir -p "${HOME}/.config/assistant-button/"
cp "${HOME}/.git/fastflx1/configs/assistant-button/*" "${HOME}/.config/assistant-button/"

mkdir -p "${HOME}/.config/feedbackd/"
cp "${HOME}/.git/fastflx1/configs/feedbackd/*" "${HOME}/.config/feedbackd/"

mkdir -p "${HOME}/.config/gtk-3.0/"
cp "${HOME}/.git/fastflx1/configs/gtk-3.0/*" "${HOME}/.config/gtk-3.0/"


mkdir -p "${HOME}/.local/share/applications/"
mkdir -p "${HOME}/.config/autostart/"
cp "${HOME}/.git/fastflx1/files/fastflx1.desktop" "${HOME}/.local/share/applications/"
cp "${HOME}/.git/fastflx1/files/yad-icon-browser.desktop" "${HOME}/.local/share/applications/"
cp "${HOME}/.git/fastflx1/configs/autostart/alarmvol.desktop" "${HOME}/.local/share/applications/"
cp "${HOME}/.git/fastflx1/configs/autostart/dialtone.desktop" "${HOME}/.local/share/applications/"

gsettings set org.gnome.desktop.sound theme-name __custom