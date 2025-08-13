#!/bin/bash

# ==============================================================================
# FastFLX1 Setup Script
#
# Manages the installation, uninstallation, and updates of the FastFLX1
# environment customizations.
#
# USAGE:
#   sudo ./setup.sh install     - Installs all components and configs.
#   sudo ./setup.sh uninstall   - Removes all components and restores backups.
#   sudo ./setup.sh update      - Uninstalls, fetches the latest version, and reinstalls.
#
# Must be run with sudo privileges.
# ==============================================================================

# --- Configuration ---
# Get the home directory of the user who called sudo, not root's home.
if [ -n "$SUDO_USER" ]; then
    USER_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
else
    # Fallback for running without sudo (though the script requires it)
    USER_HOME=$HOME
fi

GIT_DIR="${USER_HOME}/.git/fastflx1"
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

    # 1. Install required packages (won't be removed by uninstall).
    echo "--> Installing APT packages..."
    apt install -y wtype curl wl-clipboard inotify-tools lisgd libcallaudio-tools wofi libnotify-bin bindfs wlrctl libpam-parallel libpam-biomd

    # 2. Set permissions for update script.
    echo "--> Setting permissions for helper scripts..."
    chmod +x "${GIT_DIR}/update.sh"

    # 3. Copy scripts to /usr/bin.
    echo "--> Copying system scripts to /usr/bin..."
    for script in "${SCRIPTS_TO_INSTALL[@]}"; do
        cp "${GIT_DIR}/scripts/${script}" "/usr/bin/"
        chmod +x "/usr/bin/${script}"
    done

    # 4. Copy all user configuration files.
    echo "--> Copying user configuration files to ${USER_HOME}..."
    mkdir -p "${USER_HOME}/.config/assistant-button"
    cp "${GIT_DIR}/configs/assistant-button/"{short_press,double_press,long_press} "${USER_HOME}/.config/assistant-button/"

    mkdir -p "${USER_HOME}/.config/feedbackd/themes"
    cp "${GIT_DIR}/configs/feedbackd/themes/default.json" "${USER_HOME}/.config/feedbackd/themes"

    mkdir -p "${USER_HOME}/.config/gtk-3.0"
    cp "${GIT_DIR}/configs/gtk-3.0/gtk.css" "${USER_HOME}/.config/gtk-3.0/"

    mkdir -p "${USER_HOME}/.config/wofi"
    cp "${GIT_DIR}/configs/wofi/"{style.css,config} "${USER_HOME}/.config/wofi/"

    # 5. Handle squeekboard keyboards.
    echo "--> Setting up squeekboard keyboards..."
    keyboard_dir="${USER_HOME}/.local/share/squeekboard/keyboards"
    mkdir -p "${keyboard_dir}"
    for subdir in email emoji number pin terminal url; do
        mkdir -p "${keyboard_dir}/${subdir}"
        cp "${GIT_DIR}/share/fi.yaml" "${keyboard_dir}/${subdir}/"
    done
    cp "${GIT_DIR}/share/fi.yaml" "${keyboard_dir}/"

    # 6. Handle custom sounds and applications.
    echo "--> Setting up custom sounds and application files..."
    sound_dir="${USER_HOME}/.local/share/sounds/__custom"
    mkdir -p "${sound_dir}"
    cp "${GIT_DIR}/share/"{alarm-clock-elapsed.oga,audio-volume-change.oga,index.theme} "${sound_dir}/"

    app_dir="${USER_HOME}/.local/share/applications"
    autostart_dir="${USER_HOME}/.config/autostart"
    mkdir -p "${app_dir}" "${autostart_dir}"
    cp "${GIT_DIR}/files/"*.desktop "${app_dir}/"
    cp "${GIT_DIR}/configs/autostart/"*.desktop "${autostart_dir}/"
    
    # Run chown to ensure the user owns all their config files, not root.
    echo "--> Correcting ownership of user files..."
    chown -R "${SUDO_USER}:${SUDO_USER}" "${USER_HOME}/.config" "${USER_HOME}/.local"

    # 7. Set custom sound theme.
    echo "--> Setting custom sound theme..."
    gsettings set org.gnome.desktop.sound theme-name __custom

    # 8. Configure PAM files (with backups).
    echo "--> Configuring PAM files..."
    for file in "${PAM_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo "  -> Backing up $file to $file.bak"
            cp -f "$file" "$file.bak"
        fi
    done

    # CORRECTED EMOJI in sudo config
    tee /etc/pam.d/sudo > /dev/null <<'EOF'
#%PAM-1.0
auth    sufficient pam_parallel.so debug { "mode": "One", "modules": {"biomd": "🫆", "login": "🔐"} }
@include common-auth
@include common-account
@include common-session-noninteractive
EOF

    tee /etc/pam.d/polkit-1 > /dev/null <<'EOF'
#%PAM-1.0
auth    sufficient pam_parallel.so debug { "mode": "One", "modules": {"biomd": "🫆", "login": "🔐"} }
@include common-auth
@include common-account
@include common-password
session         required    pam_env.so readenv=1 user_readenv=0
session         required    pam_env.so readenv=1 envfile=/etc/default/locale user_readenv=0
@include common-session-noninteractive
EOF

    tee /etc/pam.d/biomd > /dev/null <<'EOF'
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
            mv -f "$file.bak" "$file"
        else
            echo "  -> No backup found for $file. Removing the file."
            rm -f "$file"
        fi
    done

    # 2. Remove system scripts.
    echo "--> Removing system scripts from /usr/bin..."
    for script in "${SCRIPTS_TO_INSTALL[@]}"; do
        rm -f "/usr/bin/${script}"
    done

    # 3. Remove all copied user configuration files.
    echo "--> Removing user configuration files from ${USER_HOME}..."
    rm -f "${USER_HOME}/.config/assistant-button/"{short_press,double_press,long_press}
    rm -f "${USER_HOME}/.config/feedbackd/themes/default.json"
    rm -f "${USER_HOME}/.config/gtk-3.0/gtk.css"
    rm -f "${USER_HOME}/.config/wofi/"{style.css,config}
    rm -rf "${USER_HOME}/.local/share/squeekboard/keyboards"
    rm -f "${USER_HOME}/.local/share/sounds/__custom/"*
    rm -f "${USER_HOME}/.local/share/applications/"{fastflx1}.desktop
    rm -f "${USER_HOME}/.config/autostart/"{alarmvol,batterysaver,andromeda-guard,dialtone,gesture-shortcuts}.desktop

    # 4. Reset sound theme to default.
    echo "--> Resetting sound theme to default..."
    gsettings set org.gnome.desktop.sound theme-name 'default'

    echo "--- Uninstallation Complete ---"
}

# Function to perform an update.
do_update() {
    echo "--- Starting FastFLX1 Update ---"
    
    # 1. Uninstall the current version to ensure a clean state.
    do_uninstall
    
    # 2. Remove the old repository.
    echo "--> Removing old repository at ${GIT_DIR}..."
    rm -rf "${GIT_DIR}"
    
    # 3. Install git and re-clone the repository.
    echo "--> Installing git and cloning latest version..."
    apt install -y git
    # Clone into the user's home directory, not root's.
    # We run the git clone command as the original user to handle SSH keys etc. correctly.
    sudo -u "$SUDO_USER" git clone https://gitlab.com/Alaraajavamma/fastflx1 "${GIT_DIR}"
    
    # 4. Re-run the installation with the new files.
    echo "--> Running installation with new files..."
    do_install
    
    echo "--- Update Process Finished ---"
}


# --- Main Script Logic ---

# Check for root privileges.
if [ -z "$SUDO_USER" ] || [ "$(id -u)" -ne 0 ]; then
    error "This script must be run with sudo. Usage: sudo ./setup.sh <action>"
fi

# Check for a valid action.
ACTION=$1
if [ -z "$ACTION" ]; then
    echo "Usage: sudo $0 {install|uninstall|update}"
    exit 1
fi

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

exit 0

