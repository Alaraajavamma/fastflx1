#!/bin/bash

# ==============================================================================
# FastFLX1 Setup Script
#
# Manages the installation, uninstallation, and updates of the FastFLX1
# environment customizations.
#
# USAGE:
#   ./setup.sh install     - Installs all components and configs.
#   ./setup.sh uninstall   - Removes all components and restores backups.
#   ./setup.sh update      - Uninstalls, fetches the latest version, and reinstalls.
#
# This script should be run as a regular user. It will prompt for sudo
# privileges when needed.
# ==============================================================================

# --- Configuration ---
# The script now runs as the user, so ${HOME} is correct.
GIT_DIR="${HOME}/.git/fastflx1"
PAM_FILES=("/etc/pam.d/sudo" "/etc/pam.d/polkit-1" "/etc/pam.d/biomd")
SCRIPTS_TO_INSTALL=(
    "alarmvol" "double-press" "fastflx1" "gnome-weather-location"
    "long-press" "short-press" "gesture-shortcuts"
    "andromeda-guard" "andromeda-shared-folders"
)

# --- Helper Functions ---

# Function to display an error message and exit.
error() {
    echo "ERROR: $1" >&2
    exit 1
}

# Function to perform the installation.
do_install() {
    echo "--- Starting FastFLX1 Installation ---"

    # 1. Install required packages.
    echo "--> Installing APT packages..."
    sudo apt install -y wtype curl wl-clipboard inotify-tools lisgd libcallaudio-tools wofi libnotify-bin bindfs wlrctl libpam-parallel libpam-biomd acl

    # 2. Copy scripts to /usr/bin.
    echo "--> Copying system scripts to /usr/bin..."
    for script in "${SCRIPTS_TO_INSTALL[@]}"; do
        sudo cp "${GIT_DIR}/scripts/${script}" "/usr/bin/"
        sudo chmod +x "/usr/bin/${script}"
    done

    # 3. Copy all user configuration files (no sudo needed).
    echo "--> Copying user configuration files to ${HOME}..."
    mkdir -p "${HOME}/.config/assistant-button"
    cp "${GIT_DIR}/configs/assistant-button/"{short_press,double_press,long_press} "${HOME}/.config/assistant-button/"

    mkdir -p "${HOME}/.config/gtk-3.0"
    cp "${GIT_DIR}/configs/gtk-3.0/gtk.css" "${HOME}/.config/gtk-3.0/"

    mkdir -p "${HOME}/.config/wofi"
    cp "${GIT_DIR}/configs/wofi/"{style.css,config} "${HOME}/.config/wofi/"

    # 4. Handle squeekboard keyboards.
    echo "--> Copying whole squeekboard keyboards folder..."
    
    # Define the source folder containing the keyboards
    SOURCE_SQUEEKBOARD_DIR="${GIT_DIR}/share/squeekboard"
    
    # Define the destination folder: $HOME/.local/share/squeekboard/
    DEST_SQUEEKBOARD_PARENT_DIR="${HOME}/.local/share/"
    
    # Ensure the parent destination directory exists (if not already created by step 5)
    mkdir -p "${DEST_SQUEEKBOARD_PARENT_DIR}"
    
    # Use 'cp -r' to recursively copy the entire 'squeekboard' folder and its contents
    # from the git directory to the $HOME/.local/share/ location.
    # This will create $HOME/.local/share/squeekboard/ and everything inside it.
    cp -r "${SOURCE_SQUEEKBOARD_DIR}" "${DEST_SQUEEKBOARD_PARENT_DIR}"

    # 5. Handle custom sounds and applications.
    echo "--> Setting up custom sounds and application files..."
    sound_dir="${HOME}/.local/share/sounds/__custom"
    mkdir -p "${sound_dir}"
    cp "${GIT_DIR}/share/sounds/__custom/"{alarm-clock-elapsed.oga,audio-volume-change.oga,index.theme} "${sound_dir}/"

    app_dir="${HOME}/.local/share/applications"
    autostart_dir="${HOME}/.config/autostart"
    mkdir -p "${app_dir}" "${autostart_dir}"
    cp "${GIT_DIR}/files/"*.desktop "${app_dir}/"
    cp "${GIT_DIR}/configs/autostart/"*.desktop "${autostart_dir}/"

    # 6. Set custom sound theme (no sudo needed).
    echo "--> Setting custom sound theme..."
    gsettings set org.gnome.desktop.sound theme-name __custom

    # 7. Configure PAM files (with backups).
    echo "--> Configuring PAM files..."
    for file in "${PAM_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo "  -> Backing up $file to $file.bak"
            sudo cp -f "$file" "$file.bak"
        fi
    done

    sudo tee /etc/pam.d/sudo > /dev/null <<'EOF'
#%PAM-1.0
auth    sufficient pam_parallel.so debug { "mode": "One", "modules": {"biomd": " 🫆 ", "login": " 🔐 "} }
@include common-auth
@include common-account
@include common-session-noninteractive
EOF

    sudo tee /etc/pam.d/polkit-1 > /dev/null <<'EOF'
#%PAM-1.0
auth    sufficient pam_parallel.so debug { "mode": "One", "modules": {"biomd": " 🫆 ", "login": " 🔐 "} }
@include common-auth
@include common-account
@include common-password
session         required    pam_env.so readenv=1 user_readenv=0
session         required    pam_env.so readenv=1 envfile=/etc/default/locale user_readenv=0
@include common-session-noninteractive
EOF

    sudo tee /etc/pam.d/biomd > /dev/null <<'EOF'
auth    requisite       pam_biomd.so debug
account required        pam_permit.so
EOF

    echo "--- Installation Complete ---"
}

# Function to perform the uninstallation.
do_uninstall() {
    echo "--- Starting FastFLX1 Uninstallation ---"

    # 1. Restore PAM files from backups.
    echo "--> Restoring original PAM files..."
    for file in "${PAM_FILES[@]}"; do
        if [ -f "$file.bak" ]; then
            echo "  -> Restoring $file from backup..."
            sudo mv -f "$file.bak" "$file"
        else
            echo "  -> No backup found for $file. Removing the file."
            sudo rm -f "$file"
        fi
    done

    # 2. Remove system scripts.
    echo "--> Removing system scripts from /usr/bin..."
    for script in "${SCRIPTS_TO_INSTALL[@]}"; do
        sudo rm -f "/usr/bin/${script}"
    done

    # 3. Remove all copied user configuration files (no sudo needed).
    echo "--> Removing user configuration files from ${HOME}..."
    rm -f "${HOME}/.config/assistant-button/"{short_press,double_press,long_press}
    rm -f "${HOME}/.config/gtk-3.0/gtk.css"
    rm -f "${HOME}/.config/wofi/"{style.css,config}
    rm -rf "${HOME}/.local/share/squeekboard/keyboards"
    rm -f "${HOME}/.local/share/sounds/__custom/"*
    rm -f "${HOME}/.local/share/applications/"{fastflx1}.desktop
    rm -f "${HOME}/.config/autostart/"{alarmvol,andromeda-guard,gesture-shortcuts}.desktop

    # 4. Reset sound theme to default (no sudo needed).
    echo "--> Resetting sound theme to default..."
    gsettings set org.gnome.desktop.sound theme-name 'default'

    # 5. Remove the git repository directory.
    echo "--> Removing git repository..."
    rm -rf "${GIT_DIR}"

    echo "--- Uninstallation Complete ---"
}

# Function to perform an update.
do_update() {
    echo "--- Starting FastFLX1 Update ---"

    cd "${HOME}" || error "Could not change to home directory."

    # 1. Uninstall the current version to ensure a clean state.
    echo "--> Uninstalling the current version for a clean update..."
    do_uninstall

    # 2. Install git and clone the latest version from the repository.
    echo "--> Installing git and cloning the latest version..."
    sudo apt install -y git
    git clone https://gitlab.com/Alaraajavamma/fastflx1 "${GIT_DIR}" || error "Failed to clone the repository."

    # 3. Hand over execution to the new setup script to run the install.
    # The 'exec' command replaces this script's process with the new one.
    local new_script="${GIT_DIR}/setup.sh"
    echo "--> Making the new setup script executable..."
    chmod +x "${new_script}" || error "Failed to make the new script executable."

    echo "--> Handing over to the new setup script for installation..."
    exec "${new_script}" install
}


# --- Main Script Logic ---

# ADDED: Prevent script from being run as root.
if [ "$(id -u)" -eq 0 ]; then
    error "This script must not be run as root. Run it as a regular user without sudo."
fi

# Check if an action was provided.
ACTION=$1
if [ -z "$ACTION" ]; then
    echo "Usage: $0 {install|uninstall|update}"
    exit 1
fi

# Prompt for the sudo password once at the beginning and keep it alive.
echo "This script needs to run some commands as root."
sudo -v
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# Execute the chosen action.
case "$ACTION" in
    install)
        do_install
        ;;
    uninstall)
        do_uninstall
        ;;
    update)
        do_update
        ;;
    *)
        error "Invalid action '$ACTION'. Use 'install', 'uninstall', or 'update'."
        ;;
esac

# Ask for reboot after install or update.
# This part will be reached by the 'install' action.
# When 'update' is run, the 'exec' command hands off control, and the new
# script will run this section after it completes its 'install' step.
if [ "$ACTION" == "install" ] || [ "$ACTION" == "update" ]; then
    echo -n "To finish setup, we need to reboot. Reboot now? Type 'Yes' to confirm: "
    read answer
    if [ "$answer" == "Yes" ]; then
        echo "Rebooting..."
        sudo reboot
    else
        echo "Reboot canceled. Please reboot manually later."
    fi
fi

exit 0