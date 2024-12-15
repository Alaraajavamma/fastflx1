#!/bin/bash
sudo apt update && sudo apt upgrade -y
sudo apt update && sudo apt upgrade -y
sudo apt update && sudo apt upgrade -y
sudo apt instalĺ -y wtype yad
cp -r /home/furios/.git/fastflx1/configs/* /home/furios/.config/
cp -r /home/furios/.git/fastflx1/share/* /home/furios/.local/share/
sudo chmod +x /home/furios/.git/fastflx1/uninstall.sh
sudo chmod +x /home/furios/.git/fastflx1/update.sh
sudo chmod +x /home/furios/.git/fastflx1/scripts/*
sudo cp /home/furios/.git/fastflx1/scripts/* /usr/bin/
sudo chmod +x /usr/bin/alarmvol
sudo chmod +x /usr/bin/dialtone
sudo chmod +x /usr/bin/double-press
sudo chmod +x /usr/bin/fastflx1
sudo chmod +x /usr/bin/gnome-weather-location
sudo chmod +x /usr/bin/long-press
sudo chmod +x /usr/bin/short-press
sudo chmod +x /usr/bin/squeekboard-scale
cp /home/furios/.git/fastflx1/files/fastflx1.desktop /home/furios/.local/share/applications/
cp /home/furios/.git/fastflx1/files/yad-icon-browser.desktop /home/furios/.local/share/applications/
cp /home/furios/.git/fastflx1/configs/alarmvol.desktop /home/furios/.config/autostart/
cp /home/furios/.git/fastflx1/configs/dialtone.desktop /home/furios/.config/autostart/
gsettings set org.gnome.desktop.sound theme-name __custom