#!/bin/bash
rm ~/.local/share/applications/fastflx1.desktop
rm ~/.local/share/applications/yad-icon-browser.desktop
rm ~/.local/share/applications/display-im6.q16.desktop
rm ~/.config/autostart/dialtone.desktop
rm ~/.config/autostart/alarmvol.desktop
rm ~/.config/autostart/gen-thumbnails.desktop
rm ~/.config/autostart/gesture-shortcuts.desktop
rm ~/.config/autostart/vol-buttons.desktop
rm ~/.config/gtk-3.0/gtk.css
rm -rf ~/.config/feedbackd
rm -rf ~/.config/assistant-button
rm -rf ~/.local/share/squeekboard
rm -rf ~/.local/share/sounds
sudo rm /usr/bin/alarmvol
sudo rm /usr/bin/dialtone
sudo rm /usr/bin/double-press
sudo rm /usr/bin/gen-thumbnails
sudo rm /usr/bin/fastflx1
sudo rm /usr/bin/gnome-weather-location
sudo rm /usr/bin/gesture-shortcuts
sudo rm /usr/bin/long-press
sudo rm /usr/bin/short-press
sudo rm /usr/bin/squeekboard-scale
sudo rm /usr/bin/vol-buttons
sudo apt remove yad wl-clipboard inotify-tools imagemagick lisgd evtest
gsettings set org.gnome.desktop.sound theme-name default
cd ~ && rm -rf .git/fastflx1
