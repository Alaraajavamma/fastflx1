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
    "alarmvol" "dialtone" "double-press" "fastflx1" "gnome-weather-location"
    "long-press" "short-press" "batterysaver" "gesture-shortcuts"
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
    sudo apt install -y wtype curl wl-clipboard inotify-tools lisgd libcallaudio-tools wofi libnotify-bin bindfs wlrctl libpam-parallel libpam-biomd

    # 2. Set permissions for update script (no sudo needed).
    echo "--> Setting permissions for helper scripts..."
    chmod +x "${GIT_DIR}/update.sh"

    # 3. Copy scripts to /usr/bin.
    echo "--> Copying system scripts to /usr/bin..."
    for script in "${SCRIPTS_TO_INSTALL[@]}"; do
        sudo cp "${GIT_DIR}/scripts/${script}" "/usr/bin/"
        sudo chmod +x "/usr/bin/${script}"
    done

    # 4. Copy all user configuration files (no sudo needed).
    echo "--> Copying user configuration files to ${HOME}..."
    mkdir -p "${HOME}/.config/assistant-button"
    cp "${GIT_DIR}/configs/assistant-button/"{short_press,double_press,long_press} "${HOME}/.config/assistant-button/"

    mkdir -p "${HOME}/.config/feedbackd/themes"
    cp "${GIT_DIR}/configs/feedbackd/themes/default.json" "${HOME}/.config/feedbackd/themes"

    mkdir -p "${HOME}/.config/gtk-3.0"
    cp "${GIT_DIR}/configs/gtk-3.0/gtk.css" "${HOME}/.config/gtk-3.0/"

    mkdir -p "${HOME}/.config/wofi"
    cp "${GIT_DIR}/configs/wofi/"{style.css,config} "${HOME}/.config/wofi/"

    # 5. Handle squeekboard keyboards.
    echo "--> Setting up squeekboard keyboards..."
    keyboard_dir="${HOME}/.local/share/squeekboard/keyboards"
    mkdir -p "${keyboard_dir}"
    for subdir in email emoji number pin terminal url; do
        mkdir -p "${keyboard_dir}/${subdir}"
        cp "${GIT_DIR}/share/fi.yaml" "${keyboard_dir}/${subdir}/"
    done
    cp "${GIT_DIR}/share/fi.yaml" "${keyboard_dir}/"

    # 6. Handle custom sounds and applications.
    echo "--> Setting up custom sounds and application files..."
    sound_dir="${HOME}/.local/share/sounds/__custom"
    mkdir -p "${sound_dir}"
    cp "${GIT_DIR}/share/"{alarm-clock-elapsed.oga,audio-volume-change.oga,index.theme} "${sound_dir}/"

    app_dir="${HOME}/.local/share/applications"
    autostart_dir="${HOME}/.config/autostart"
    mkdir -p "${app_dir}" "${autostart_dir}"
    cp "${GIT_DIR}/files/"*.desktop "${app_dir}/"
    cp "${GIT_DIR}/configs/autostart/"*.desktop "${autostart_dir}/"

    # 7. Set custom sound theme (no sudo needed).
    echo "--> Setting custom sound theme..."
    gsettings set org.gnome.desktop.sound theme-name __custom

    # 8. Configure PAM files (with backups).
    echo "--> Configuring PAM files..."
    for file in "${PAM_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo "  -> Backing up $file to $file.bak"
            sudo cp -f "$file" "$file.bak"
        fi
    done

    sudo tee /etc/pam.d/sudo > /dev/null <<'EOF'
#%PAM-1.0
auth    sufficient pam_parallel.so debug { "mode": "One", "modules": {"biomd": "🫆", "login": "🔐"} }
@include common-auth
@include common-account
@include common-session-noninteractive
EOF

    sudo tee /etc/pam.d/polkit-1 > /dev/null <<'EOF'
#%PAM-1.0
auth    sufficient pam_parallel.so debug { "mode": "One", "modules": {"biomd": "🫆", "login": "🔐"} }
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
    rm -f "${HOME}/.config/feedbackd/themes/default.json"
    rm -f "${HOME}/.config/gtk-3.0/gtk.css"
    rm -f "${HOME}/.config/wofi/"{style.css,config}
    rm -rf "${HOME}/.local/share/squeekboard/keyboards"
    rm -f "${HOME}/.local/share/sounds/__custom/"*
    rm -f "${HOME}/.local/share/applications/"{fastflx1}.desktop
    rm -f "${HOME}/.config/autostart/"{alarmvol,batterysaver,andromeda-guard,dialtone,gesture-shortcuts}.desktop

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
    
    # 1. Uninstall the current version to ensure a clean state.
    do_uninstall
    
    # 2. Install git and re-clone the repository.
    echo "--> Installing git and cloning latest version..."
    sudo apt install -y git
    git clone https://gitlab.com/Alaraajavamma/fastflx1 "${GIT_DIR}"
    
    # 3. Re-run the installation with the new files.
    echo "--> Running installation with new files..."
    do_install
    
    echo "--- Update Process Finished ---"
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

