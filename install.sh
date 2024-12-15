#!/bin/bash
sudo apt update && sudo apt upgrade -y --allow-downgrades
sudo apt update && sudo apt upgrade -y --allow-downgrades
sudo apt update && sudo apt upgrade -y --allow-downgrades
sudo apt instal ĺ -y wtype yad
cp -r "${HOME}/.git/fastflx1/configs/* "${HOME}/.config/"
cp -r "${HOME}/.git/fastflx1/share/* "${HOME}/.local/share/"
sudo chmod +x "${HOME}/.git/fastflx1/uninstall.sh"
sudo chmod +x "${HOME}/.git/fastflx1/update.sh"
sudo chmod +x "${HOME}/.git/fastflx1/scripts/*"
sudo cp "${HOME}/.git/fastflx1/scripts/*" /usr/bin/
sudo chmod +x /usr/bin/alarmvol
sudo chmod +x /usr/bin/dialtone
sudo chmod +x /usr/bin/double-press
sudo chmod +x /usr/bin/fastflx1
sudo chmod +x /usr/bin/gnome-weather-location
sudo chmod +x /usr/bin/long-press
sudo chmod +x /usr/bin/short-press
sudo chmod +x /usr/bin/squeekboard-scale
cp "${HOME}/.git/fastflx1/files/fastflx1.desktop" "${HOME}/.local/share/applications/fastflx1.desktop"
cp "${HOME}/.git/fastflx1/files/yad-icon-browser.desktop" "${HOME}/.local/share/applications/yad-icon-browser.desktop"
cp "${HOME}/.git/fastflx1/configs/alarmvol.desktop" "${HOME}/.config/autostart/alarmvol.desktop"
cp "${HOME}/.git/fastflx1/configs/dialtone.desktop" "${HOME}/.config/autostart/dialtone.desktop"
gsettings set org.gnome.desktop.sound theme-name __custom