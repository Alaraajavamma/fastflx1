#!/bin/bash
rm ~/.local/share/applications/fastdial.desktop
rm ~/.local/share/applications/yad-icon-browser.desktop
rm ~/.config/autostart/fasthistory.desktop
rm ~/.config/gtk-3.0/gtk.css
rm -rf ~/.config/feedbackd
rm -rf ~/.config/assistant-button
rm -rf ~/.local/share/squeekboard
sudo rm /usr/bin/alarmvol
sudo rm /usr/bin/dialtone
sudo rm /usr/bin/double-press
sudo rm /usr/bin/fastflx1
sudo rm /usr/bin/gnome-weather-location
sudo rm /usr/bin/long-press
sudo rm /usr/bin/short-press
sudo rm /usr/bin/squeekboard-scale
sudo apt remove yad
gsettings set org.gnome.desktop.sound theme-name default
cd ~ && rm -rf .git/fastflx1
sudo rm -rf /opt/fastflx1