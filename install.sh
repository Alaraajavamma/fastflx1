#!/bin/bash

echo "FastFLX1: A convenient way to enhance your FLX1 device with custom features and workarounds."

# Update system and apply upgrades
sudo apt update && sudo apt upgrade -y --allow-downgrades

# Install required packages
sudo apt install -y wtype yad

# Create necessary directories
declare -a dirs=(
    "${HOME}/.config/autostart"
    "${HOME}/.config/assistant-button"
    "${HOME}/.config/feedbackd"
    "${HOME}/.config/gtk-3.0"
    "${HOME}/.local/share/applications"
    "${HOME}/.local/share/sounds/__custom"
    "${HOME}/.local/share/squeekboard/keyboards"
    "${HOME}/.local/share/squeekboard/keyboards/email"
    "${HOME}/.local/share/squeekboard/keyboards/emoji"
    "${HOME}/.local/share/squeekboard/keyboards/number"
    "${HOME}/.local/share/squeekboard/keyboards/pin"
    "${HOME}/.local/share/squeekboard/keyboards/terminal"
    "${HOME}/.local/share/squeekboard/keyboards/url"
)

for dir in "${dirs[@]}"; do
    mkdir -p "$dir"
done

# Ensure the scripts are executable
chmod +x "${HOME}/.git/fastflx1/uninstall.sh"
chmod +x "${HOME}/.git/fastflx1/update.sh"
chmod +x "${HOME}/.git/fastflx1/scripts/*"

# Copy configuration files to the appropriate directories
cp -r "${HOME}/.git/fastflx1/configs/assistant-button/"* "${HOME}/.config/assistant-button/"
cp -r "${HOME}/.git/fastflx1/configs/autostart/"* "${HOME}/.config/autostart/"
cp -r "${HOME}/.git/fastflx1/configs/feedbackd/"* "${HOME}/.config/feedbackd/"
cp -r "${HOME}/.git/fastflx1/configs/gtk-3.0/"* "${HOME}/.config/gtk-3.0/"
cp -r "${HOME}/.git/fastflx1/share/squeekboard/"* "${HOME}/.local/share/squeekboard/"
cp -r "${HOME}/.git/fastflx1/share/sounds/"* "${HOME}/.local/share/sounds/"

# Create desktop entries
cp "${HOME}/.git/fastflx1/files/fastflx1.desktop" "${HOME}/.local/share/applications/fastflx1.desktop"
cp "${HOME}/.git/fastflx1/files/yad-icon-browser.desktop" "${HOME}/.local/share/applications/yad-icon-browser.desktop"
cp "${HOME}/.git/fastflx1/configs/alarmvol.desktop" "${HOME}/.config/autostart/alarmvol.desktop"
cp "${HOME}/.git/fastflx1/configs/dialtone.desktop" "${HOME}/.config/autostart/dialtone.desktop"

# Add FastFLX1 directories to the system's PATH
echo 'export PATH="$PATH:/home/furios/.git/fastflx1"' >> ~/.bashrc
echo 'export PATH="$PATH:/home/furios/.git/fastflx1/.git"' >> ~/.bashrc

# Reload bashrc to apply changes
source ~/.bashrc

# Set custom sound theme
gsettings set org.gnome.desktop.sound theme-name __custom

echo "FastFLX1 setup complete!"
