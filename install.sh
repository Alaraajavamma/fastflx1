#!/bin/bash

# Update and upgrade system packages
echo "Updating and upgrading system packages..."
sudo apt update && sudo apt upgrade -y || {
    echo "Failed to update or upgrade packages. Exiting." >&2
    exit 1
}

# Install required packages
echo "Installing required packages..."
sudo apt install -y wtype yad || {
    echo "Failed to install required packages. Exiting." >&2
    exit 1
}

# Define base directory and ensure it exists
BASE_DIR="/home/furios/.git/fastflx1"
if [ ! -d "$BASE_DIR" ]; then
    echo "Base directory $BASE_DIR does not exist. Exiting." >&2
    exit 1
fi

# Copy configuration and share files
echo "Copying configuration and share files..."
cp -r "$BASE_DIR/configs/"* /home/furios/.config/ || echo "Failed to copy configuration files."
cp -r "$BASE_DIR/share/"* /home/furios/.local/share/ || echo "Failed to copy share files."

# Set permissions for scripts
echo "Setting executable permissions for scripts..."
SCRIPTS=(
    "uninstall.sh"
    "update.sh"
    "scripts/*"
)
for SCRIPT in "${SCRIPTS[@]}"; do
    sudo chmod +x "$BASE_DIR/$SCRIPT" || echo "Failed to set permissions for $SCRIPT."
done

# Copy scripts to /usr/bin and set permissions
echo "Copying scripts to /usr/bin..."
sudo cp "$BASE_DIR/scripts/"* /usr/bin/ || {
    echo "Failed to copy scripts to /usr/bin. Exiting." >&2
    exit 1
}
for BIN_SCRIPT in alarmvol dialtone double-press fastflx1 gnome-weather-location long-press short-press squeekboard-scale; do
    sudo chmod +x "/usr/bin/$BIN_SCRIPT" || echo "Failed to set permissions for /usr/bin/$BIN_SCRIPT."
done

# Copy desktop entry files
echo "Copying desktop entry files..."
cp "$BASE_DIR/files/fastflx1.desktop" /home/furios/.local/share/applications/ || echo "Failed to copy fastflx1.desktop."
cp "$BASE_DIR/files/yad-icon-browser.desktop" /home/furios/.local/share/applications/ || echo "Failed to copy yad-icon-browser.desktop."

# Copy autostart configuration
echo "Copying autostart configuration..."
cp "$BASE_DIR/configs/alarmvol.desktop" /home/furios/.config/autostart/ || echo "Failed to copy alarmvol.desktop."
cp "$BASE_DIR/configs/dialtone.desktop" /home/furios/.config/autostart/ || echo "Failed to copy dialtone.desktop."

# Set GNOME desktop sound theme
echo "Setting GNOME desktop sound theme..."
if command -v gsettings >/dev/null 2>&1; then
    gsettings set org.gnome.desktop.sound theme-name "__custom" || {
        echo "Failed to set GNOME sound theme."
    }
else
    echo "gsettings not found. Skipping sound theme configuration."
fi

echo "Setup completed successfully."
