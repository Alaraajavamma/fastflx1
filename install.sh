#!/bin/bash
sudo apt install -y wtype curl wl-clipboard inotify-tools lisgd libcallaudio-tools wofi libnotify-bin bindfs

# Set permissions for uninstall and update scripts
sudo chmod +x "${HOME}/.git/fastflx1/uninstall.sh" "${HOME}/.git/fastflx1/update.sh"

# Copy scripts to /usr/bin and set permissions
for script in alarmvol dialtone double-press fastflx1 gnome-weather-location long-press short-press squeekboard-scale gesture-shortcuts andromeda-listener assistant-button-tweak ; do
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

mkdir -p "${HOME}/.config/wofi"
cp "${HOME}/.git/fastflx1/configs/wofi/style.css" "${HOME}/.config/wofi/"
cp "${HOME}/.git/fastflx1/configs/wofi/config" "${HOME}/.config/wofi/"

mkdir -p "${HOME}/.config/evremap"
cp "${HOME}/.git/fastflx1/configs/evremap/remap.toml" "${HOME}/.config/evremap/"


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
cp "${HOME}/.git/fastflx1/share/"{alarm-clock-elapsed.oga,audio-volume-change.oga,index.theme} "${sound_dir}/"

# Applications and autostart files
app_dir="${HOME}/.local/share/applications"
autostart_dir="${HOME}/.config/autostart"
mkdir -p "${app_dir}" "${autostart_dir}"
cp "${HOME}/.git/fastflx1/files/"{fastflx1.desktop,yad-icon-browser.desktop,display-im6.q16.desktop,display-im7.q16.desktop,feh.desktop} "${app_dir}/"
cp "${HOME}/.git/fastflx1/configs/autostart/"{alarmvol.desktop,andromeda-listener.desktop,dialtone.desktop,gesture-shortcuts.desktop,vol-buttons.desktop,evremap.desktop} "${autostart_dir}/"

# Set custom sound theme
gsettings set org.gnome.desktop.sound theme-name __custom

echo ""
echo "Configuring passwordless sudo for Andromeda Listener..."

# Define the user and the full paths to the commands used in the script
SUDOERS_FILE="/etc/sudoers.d/andromeda-manager"
SUDOERS_RULE="$USER ALL=(ALL) NOPASSWD: /usr/bin/umount, /usr/bin/test, /usr/bin/mount, /usr/bin/mkdir, /usr/bin/chown, /usr/bin/find"

# Use tee to write the file with sudo privileges
echo "$SUDOERS_RULE" | sudo tee "$SUDOERS_FILE" > /dev/null

# Set correct, secure permissions for the sudoers file
sudo chmod 440 "$SUDOERS_FILE"

echo "Configuration complete."
echo ""

echo -n "To start FastFLX1 we need to reboot. Reboot now? Type 'Yes' to confirm: "
read answer
if [ "$answer" == "Yes" ]; then
    echo "Rebooting the system..."
    sudo reboot
else
    echo "Reboot canceled."
fi