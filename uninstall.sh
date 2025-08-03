#!/bin/bash
rm ~/.local/share/applications/fastflx1.desktop
rm ~/.config/autostart/dialtone.desktop
rm ~/.config/autostart/alarmvol.desktop
rm ~/.config/autostart/gesture-shortcuts.desktop
rm ~/.config/autostart/andromeda-guard.desktop
rm ~/.config/autostart/batterysaver.desktop
rm ~/.config/gtk-3.0/gtk.css
rm -rf ~/.config/wofi/
rm -rf ~/.config/feedbackd
rm -rf ~/.config/evremap
rm -rf ~/.config/assistant-button
rm -rf ~/.local/share/squeekboard
rm -rf ~/.local/share/sounds
sudo rm /usr/bin/alarmvol
sudo rm /usr/bin/dialtone
sudo rm /usr/bin/batterysaver
sudo rm /usr/bin/andromeda-guard
sudo rm /usr/bin/andromeda-shared-folders
sudo rm /usr/bin/double-press
sudo rm /usr/bin/fastflx1
sudo rm /usr/bin/gnome-weather-location
sudo rm /usr/bin/gesture-shortcuts
sudo rm /usr/bin/long-press
sudo rm /usr/bin/short-press
sudo rm /usr/bin/squeekboard-scale
gsettings set org.gnome.desktop.sound theme-name default
cd ~ && rm -rf .git/fastflx1