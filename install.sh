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

# Define the udev rule
RULE="SUBSYSTEM==\"leds\", KERNEL==\"green:brightness\", MODE=\"0660\""

# Define the udev rules file
RULE_FILE="/etc/udev/rules.d/99-led-brightness.rules"

# Check if the rule file already exists
if [ ! -f "$RULE_FILE" ]; then
    echo "Creating udev rule file: $RULE_FILE"
    sudo touch "$RULE_FILE"  # Create the rule file if it doesn't exist
fi

# Add the rule to the file if it's not already present
if ! grep -Fxq "$RULE" "$RULE_FILE"; then
    echo "Adding udev rule to $RULE_FILE"
    echo "$RULE" | sudo tee -a "$RULE_FILE" > /dev/null  # Append the rule to the file
else
    echo "Udev rule already exists in $RULE_FILE"
fi

# Reload udev to apply the changes
echo "Reloading udev rules"
sudo udevadm control --reload-rules

# Optionally trigger the udev event to apply immediately
sudo udevadm trigger

echo "Udev rule added and reloaded successfully."

sudo usermod -aG system furios

sudo reboot
