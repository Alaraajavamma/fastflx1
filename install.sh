#!/bin/bash
sudo apt update
sudo apt upgrade -y
sudo apt update
sudo apt upgrade -y
sudo apt update
sudo apt upgrade -y
sudo apt install -y yad wtype 

sudo chmod +x "${HOME}/.git/fastflx1/uninstall.sh"
sudo chmod +x "${HOME}/.git/fastflx1/update.sh"

sudo cp "${HOME}/.git/fastflx1/scripts/alarmvol" /usr/bin/
sudo cp "${HOME}/.git/fastflx1/scripts/dialtone" /usr/bin/
sudo cp "${HOME}/.git/fastflx1/scripts/double-press" /usr/bin/
sudo cp "${HOME}/.git/fastflx1/scripts/fastflx1" /usr/bin/
sudo cp "${HOME}/.git/fastflx1/scripts/gnome-weather-location" /usr/bin/
sudo cp "${HOME}/.git/fastflx1/scripts/long-press" /usr/bin/
sudo cp "${HOME}/.git/fastflx1/scripts/short-press" /usr/bin/
sudo cp "${HOME}/.git/fastflx1/scripts/squeekboard-scale" /usr/bin/
sudo chmod +x /usr/bin/alarmvol
sudo chmod +x /usr/bin/dialtone
sudo chmod +x /usr/bin/double-press
sudo chmod +x /usr/bin/fastflx1
sudo chmod +x /usr/bin/gnome-weather-location
sudo chmod +x /usr/bin/long-press
sudo chmod +x /usr/bin/short-press
sudo chmod +x /usr/bin/squeekboard-scale

mkdir -p "${HOME}/.config/assistant-button/"
cp "${HOME}/.git/fastflx1/configs/assistant-button/short_press" "${HOME}/.config/assistant-button/"
cp "${HOME}/.git/fastflx1/configs/assistant-button/double_press" "${HOME}/.config/assistant-button/"
cp "${HOME}/.git/fastflx1/configs/assistant-button/long_press" "${HOME}/.config/assistant-button/"

mkdir -p "${HOME}/.config/feedbackd/themes"
cp "${HOME}/.git/fastflx1/configs/feedbackd/themes/default.json" "${HOME}/.config/feedbackd/themes"

mkdir -p "${HOME}/.config/gtk-3.0/"
cp "${HOME}/.git/fastflx1/configs/gtk-3.0/gtk.css" "${HOME}/.config/gtk-3.0/"

mkdir -p "${HOME}/.local/share/squeekboard/keyboards"
mkdir -p "${HOME}/.local/share/squeekboard/keyboards/email"
mkdir -p "${HOME}/.local/share/squeekboard/keyboards/emoji"
mkdir -p "${HOME}/.local/share/squeekboard/keyboards/number"
mkdir -p "${HOME}/.local/share/squeekboard/keyboards/pin"
mkdir -p "${HOME}/.local/share/squeekboard/keyboards/terminal"
mkdir -p "${HOME}/.local/share/squeekboard/keyboards/url"
cp "${HOME}/.git/fastflx1/share/fi.yaml" "${HOME}/.local/share/squeekboard/keyboards"
cp "${HOME}/.git/fastflx1/share/fi.yaml" "${HOME}/.local/share/squeekboard/keyboards/email"
cp "${HOME}/.git/fastflx1/share/fi.yaml" "${HOME}/.local/share/squeekboard/keyboards/emoji"
cp "${HOME}/.git/fastflx1/share/fi.yaml" "${HOME}/.local/share/squeekboard/keyboards/number"
cp "${HOME}/.git/fastflx1/share/fi.yaml" "${HOME}/.local/share/squeekboard/keyboards/pin"
cp "${HOME}/.git/fastflx1/share/fi.yaml" "${HOME}/.local/share/squeekboard/keyboards/terminal"
cp "${HOME}/.git/fastflx1/share/fi.yaml" "${HOME}/.local/share/squeekboard/keyboards/url"

mkdir -p "${HOME}/.local/share/sounds/__custom"
cp "${HOME}/.git/fastflx1/share/alarm-clock-elapsed.oga" "${HOME}/.local/share/sounds/__custom"
cp "${HOME}/.git/fastflx1/share/audio-volume-change.oga" "${HOME}/.local/share/sounds/__custom"


mkdir -p "${HOME}/.local/share/applications/"
mkdir -p "${HOME}/.config/autostart/"
cp "${HOME}/.git/fastflx1/files/fastflx1.desktop" "${HOME}/.local/share/applications/"
cp "${HOME}/.git/fastflx1/files/yad-icon-browser.desktop" "${HOME}/.local/share/applications/"
cp "${HOME}/.git/fastflx1/configs/autostart/alarmvol.desktop" "${HOME}/.local/share/applications/"
cp "${HOME}/.git/fastflx1/configs/autostart/dialtone.desktop" "${HOME}/.local/share/applications/"

gsettings set org.gnome.desktop.sound theme-name __custom