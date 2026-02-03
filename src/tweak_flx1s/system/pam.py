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
import re
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

    # --- Password Policy (libpam-pwquality) ---

    def check_pwquality_installed(self):
        """Checks if libpam-pwquality is installed."""
        try:
            run_command("dpkg -s libpam-pwquality", check=True)
            return True
        except Exception:
            return False

    def get_install_pwquality_cmd(self):
        """Returns command to install libpam-pwquality."""
        return "apt install -y libpam-pwquality"

    def get_remove_pwquality_cmd(self):
        """Returns command to remove libpam-pwquality."""
        return "apt remove -y libpam-pwquality"

    def get_password_limits(self):
        """
        Reads current password limits.
        Returns tuple (min_len, max_len).
        """
        min_len = 0
        max_len = 0
        file_path = "/etc/pam.d/common-password"

        if not os.path.exists(file_path):
             return 0, 0

        try:
            with open(file_path, "r") as f:
                content = f.read()

            # First priority: pam_pwquality
            for line in content.splitlines():
                if "pam_pwquality.so" in line and not line.strip().startswith("#"):
                     min_match = re.search(r"minlen=(\d+)", line)
                     max_match = re.search(r"maxlen=(\d+)", line)
                     if min_match: min_len = int(min_match.group(1))
                     if max_match: max_len = int(max_match.group(1))
                     return min_len, max_len

            # Fallback: pam_unix
            for line in content.splitlines():
                 if "pam_unix.so" in line and not line.strip().startswith("#"):
                      min_match = re.search(r"minlen=(\d+)", line)
                      if min_match: min_len = int(min_match.group(1))

            return min_len, max_len
        except Exception as e:
            logger.error(f"Failed to read password limits: {e}")
            return 0, 0

    def set_password_policy(self, min_len, max_len):
        """
        Updates common-password to use pam_pwquality with specified limits.
        Removes minlen from pam_unix.
        """
        file_path = "/etc/pam.d/common-password"
        backup_path = "/etc/pam.d/common-password.bak"

        if not os.path.exists(file_path):
            return f"File {file_path} not found."

        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backed up {file_path}")

            with open(file_path, "r") as f:
                lines = f.readlines()

            new_lines = []
            pwquality_line = f"password requisite pam_pwquality.so retry=3 minlen={min_len} maxlen={max_len}\n"
            pwquality_exists = False
            unix_found = False

            # First pass: check for pwquality and remove/update it
            for line in lines:
                if "pam_pwquality.so" in line and not line.strip().startswith("#"):
                    new_lines.append(pwquality_line)
                    pwquality_exists = True
                elif "pam_unix.so" in line and not line.strip().startswith("#"):
                    # Scrub minlen from pam_unix
                    new_unix_line = re.sub(r"\s*minlen=\d+", "", line).rstrip()
                    # If pwquality didn't exist, insert it before pam_unix
                    if not pwquality_exists:
                        new_lines.append(pwquality_line)
                        pwquality_exists = True
                    new_lines.append(new_unix_line + "\n")
                    unix_found = True
                else:
                    new_lines.append(line)

            if not unix_found:
                # This is unusual, but if no pam_unix, we just append or warn?
                # For safety, if we didn't insert pwquality yet (no unix line found), we probably shouldn't break the file blindly.
                logger.warning("pam_unix.so not found, appending pwquality at end?")
                if not pwquality_exists:
                     new_lines.append(pwquality_line)

            with open(file_path, "w") as f:
                f.writelines(new_lines)

            logger.info("Password policy updated.")
            return "Password policy updated successfully."

        except Exception as e:
            logger.error(f"Failed to update password policy: {e}")
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)
            return f"Error: {e}"

    def remove_configuration(self):
        """
        Removes pam_pwquality configuration from common-password.
        """
        file_path = "/etc/pam.d/common-password"
        backup_path = "/etc/pam.d/common-password.bak"

        if not os.path.exists(file_path):
            return "File not found."

        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backed up {file_path}")

            with open(file_path, "r") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                if "pam_pwquality.so" in line and not line.strip().startswith("#"):
                    continue # Remove this line
                new_lines.append(line)

            with open(file_path, "w") as f:
                f.writelines(new_lines)

            logger.info("Removed pwquality configuration.")
            return "Configuration removed successfully."

        except Exception as e:
            logger.error(f"Failed to remove configuration: {e}")
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)
            return f"Error: {e}"
