#!/bin/bash
sudo apt install -y yad wtype 

# Set permissions for uninstall and update scripts
sudo chmod +x "${HOME}/.git/fastflx1/uninstall.sh" "${HOME}/.git/fastflx1/update.sh"

# Copy scripts to /usr/bin and set permissions
for script in alarmvol dialtone double-press fastflx1 gnome-weather-location long-press short-press squeekboard-scale; do
    sudo cp "${HOME}/.git/fastflx1/scripts/${script}" "/usr/bin/"
    sudo chmod +x "/usr/bin/${script}"
done

# Create necessary config directories and copy files
mkdir -p "${HOME}/.config/assistant-button"
cp "${HOME}/.git/fastflx1/configs/assistant-button/"{short_press,double_press,long_press} "${HOME}/.config/assistant-button/"

mkdir -p "${HOME}/.config/feedbackd/themes"
cp "${HOME}/.git/fastflx1/configs/feedbackd/themes/default.json" "${HOME}/.config/feedbackd/themes"

mkdir -p "${HOME}/.config/gtk-3.0"
cp "${HOME}/.git/fastflx1/configs/gtk-3.0/gtk.css" "${HOME}/.config/gtk-3.0/"

# Handle squeekboard keyboards
keyboard_dir="${HOME}/.local/share/squeekboard/keyboards"
mkdir -p "${keyboard_dir}" # Base directory
for subdir in email emoji number pin terminal url; do
    mkdir -p "${keyboard_dir}/${subdir}"
    cp "${HOME}/.git/fastflx1/share/fi.yaml" "${keyboard_dir}/${subdir}/"
done
cp "${HOME}/.git/fastflx1/share/fi.yaml" "${keyboard_dir}/"

# Custom sounds directory
sound_dir="${HOME}/.local/share/sounds/__custom"
mkdir -p "${sound_dir}"
cp "${HOME}/.git/fastflx1/share/"{alarm-clock-elapsed.oga,audio-volume-change.oga} "${sound_dir}/"

# Applications and autostart files
app_dir="${HOME}/.local/share/applications"
autostart_dir="${HOME}/.config/autostart"
mkdir -p "${app_dir}" "${autostart_dir}"
cp "${HOME}/.git/fastflx1/files/"{fastflx1.desktop,yad-icon-browser.desktop} "${app_dir}/"
cp "${HOME}/.git/fastflx1/configs/autostart/"{alarmvol.desktop,dialtone.desktop} "${autostart_dir}/"

# Set custom sound theme
gsettings set org.gnome.desktop.sound theme-name __custom

sudo usermod -aG system furios

sudo reboot
