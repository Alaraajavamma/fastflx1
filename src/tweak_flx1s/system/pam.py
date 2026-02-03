# Copyright (C) 2026 alaraajavamma aki@urheiluaki.fi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import shutil
from loguru import logger
from tweak_flx1s.utils import run_command, get_device_model

class PamManager:
    """
    Manages PAM configurations for Fingerprint and Password Policy.
    Requires ROOT privileges for all operations.
    """

    PAM_FILES = {
        "sudo": "/etc/pam.d/sudo",
        "polkit-1": "/etc/pam.d/polkit-1",
        "biomd": "/etc/pam.d/biomd"
    }

    SUDO_CONTENT = """#%PAM-1.0
auth    sufficient pam_parallel.so debug { "mode": "One", "modules": {"biomd": " 🫆 ", "login": " 🔐 "} }
@include common-auth
@include common-account
@include common-session-noninteractive
"""

    POLKIT_CONTENT = """#%PAM-1.0
auth    sufficient pam_parallel.so debug { "mode": "One", "modules": {"biomd": " 🫆 ", "login": " 🔐 "} }
@include common-auth
@include common-account
@include common-password
session         required    pam_env.so readenv=1 user_readenv=0
session         required    pam_env.so readenv=1 envfile=/etc/default/locale user_readenv=0
@include common-session-noninteractive
"""

    BIOMD_CONTENT = """auth    requisite       pam_biomd.so debug
account required        pam_permit.so
"""

    COMMON_PASSWORD_BLOCK = """# /etc/pam.d/common-password - password-related modules common to all services
#
# This file is included from other service-specific PAM config files,
# and should contain a list of modules that define the services to be
# used to change user passwords.  The default is pam_unix.

# Explanation of pam_unix options:
# The "yescrypt" option enables
#hashed passwords using the yescrypt algorithm, introduced in Debian
#11.  Without this option, the default is Unix crypt.  Prior releases
#used the option "sha512"; if a shadow password hash will be shared
#between Debian 11 and older releases replace "yescrypt" with "sha512"
#for compatibility .  The "obscure" option replaces the old
#`OBSCURE_CHECKS_ENAB' option in login.defs.  See the pam_unix manpage
#for other options.

# As of pam 1.0.1-6, this file is managed by pam-auth-update by default.
# To take advantage of this, it is recommended that you configure any
# local modules either before or after the default block, and use
# pam-auth-update to manage selection of other modules.  See
# pam-auth-update(8) for details.

# here are the per-package modules (the "Primary" block)
password  [success=1 default=ignore]  pam_unix.so obscure yescrypt minlen=1
# here's the fallback if no module succeeds
password  requisite      pam_deny.so
# prime the stack with a positive return value if there isn't one already;
# this avoids us returning an error just because nothing sets a success code
# since the modules above will each just jump around
password  required      pam_permit.so
# and here are more per-package modules (the "Additional" block)
password  optional  pam_gnome_keyring.so
# end of pam-auth-update config
"""

    def configure_fingerprint(self):
        """
        Configures fingerprint authentication for FuriPhoneFLX1.
        Installs packages and updates PAM files.
        """
        model = get_device_model()
        if model != "FuriPhoneFLX1":
            logger.warning(f"Fingerprint configuration not supported on {model}")
            return "Operation not supported on this device."

        logger.info("Configuring Fingerprint Authentication...")

        logger.info("Installing required packages...")
        try:
            run_command(["apt-get", "install", "-y", "libpam-parallel", "libpam-biomd"])
        except Exception as e:
            logger.error(f"Failed to install packages: {e}")
            return f"Failed to install packages: {e}"

        for name, path in self.PAM_FILES.items():
            try:
                if os.path.exists(path):
                    shutil.copy2(path, f"{path}.bak")
                    logger.info(f"Backed up {path}")

                content = ""
                if name == "sudo": content = self.SUDO_CONTENT
                elif name == "polkit-1": content = self.POLKIT_CONTENT
                elif name == "biomd": content = self.BIOMD_CONTENT

                with open(path, "w") as f:
                    f.write(content)
                logger.info(f"Updated {path}")
            except Exception as e:
                logger.error(f"Failed to update {path}: {e}")
                return f"Failed to update {path}: {e}"

        return "Fingerprint authentication configured successfully."

    def check_fingerprint_status(self):
        """Checks if fingerprint is configured in PAM."""
        try:
            with open("/etc/pam.d/sudo", "r") as f:
                content = f.read()
                return "pam_parallel.so" in content
        except Exception:
            return False

    def remove_fingerprint_configuration(self):
        """Restores PAM configuration to defaults (removes fingerprint)."""
        logger.info("Removing Fingerprint Authentication...")
        for name, path in self.PAM_FILES.items():
            backup = f"{path}.bak"
            if os.path.exists(backup):
                try:
                    shutil.copy2(backup, path)
                    logger.info(f"Restored {path} from backup")
                except Exception as e:
                    logger.error(f"Failed to restore {path}: {e}")
                    return f"Failed to restore {path}: {e}"
            else:
                logger.warning(f"No backup found for {path}, cannot safely restore.")

        return "Fingerprint configuration removed (restored backups)."

    # --- Short Password Logic ---

    def enable_short_passwords(self):
        """
        Enables short passwords by rewriting /etc/pam.d/common-password
        with a custom configuration containing 'minlen=1'.
        """
        file_path = "/etc/pam.d/common-password"
        backup_path = "/etc/pam.d/common-password.bak"

        try:
            if not os.path.exists(backup_path) and os.path.exists(file_path):
                shutil.copy2(file_path, backup_path)
                logger.info(f"Created backup of {file_path}")

            with open(file_path, "w") as f:
                f.write(self.COMMON_PASSWORD_BLOCK)

            logger.info("Short passwords enabled.")
            return "Short passwords enabled."
        except Exception as e:
            logger.error(f"Failed to enable short passwords: {e}")
            return f"Error: {e}"

    def disable_short_passwords(self):
        """
        Disables short passwords.
        Tries to restore from backup. If no backup, rewrites the block
        removing 'minlen=1' to be safe.
        """
        file_path = "/etc/pam.d/common-password"
        backup_path = "/etc/pam.d/common-password.bak"

        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)
                logger.info(f"Restored {file_path} from backup")
                return "Short passwords disabled (restored backup)."
            else:
                logger.warning("No backup found, rewriting block without minlen=1")
                """Remove minlen=1 from the block"""
                safe_block = self.COMMON_PASSWORD_BLOCK.replace(" minlen=1", "")
                with open(file_path, "w") as f:
                    f.write(safe_block)
                return "Short passwords disabled (safe fallback)."
        except Exception as e:
            logger.error(f"Failed to disable short passwords: {e}")
            return f"Error: {e}"

    def check_short_passwords_enabled(self):
        """Checks if minlen=1 is present in common-password."""
        file_path = "/etc/pam.d/common-password"
        try:
            if not os.path.exists(file_path):
                return False
            with open(file_path, "r") as f:
                content = f.read()
            return "minlen=1" in content
        except Exception as e:
            logger.error(f"Failed to check password status: {e}")
            return False
