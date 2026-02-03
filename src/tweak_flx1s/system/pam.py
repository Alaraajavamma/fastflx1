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

    def get_min_password_length(self):
        """Reads current minimum password length."""
        # Try pwquality.conf first
        pwquality_conf = "/etc/security/pwquality.conf"
        if os.path.exists(pwquality_conf):
            try:
                with open(pwquality_conf, "r") as f:
                    for line in f:
                        if line.strip().startswith("minlen"):
                             parts = line.split("=")
                             if len(parts) > 1:
                                 return int(parts[1].strip())
            except Exception as e:
                logger.error(f"Failed to read pwquality.conf: {e}")

        # Fallback to common-password
        file_path = "/etc/pam.d/common-password"
        if not os.path.exists(file_path):
             return 0

        try:
            with open(file_path, "r") as f:
                content = f.read()

            for line in content.splitlines():
                 if "pam_unix.so" in line and not line.strip().startswith("#"):
                      match = re.search(r"minlen=(\d+)", line)
                      if match:
                          return int(match.group(1))
            return 0
        except Exception as e:
            logger.error(f"Failed to read password length: {e}")
            return 0

    def set_min_password_length(self, length):
        """
        Updates configuration to set minimum password length.
        """
        logger.info(f"Setting minimum password length to {length}...")

        pwquality_conf = "/etc/security/pwquality.conf"
        if os.path.exists(pwquality_conf):
            return self._update_pwquality_conf(pwquality_conf, length)
        else:
            return self._update_pam_unix(length)

    def _update_pwquality_conf(self, path, length):
        try:
            backup = f"{path}.bak"
            shutil.copy2(path, backup)
            logger.info(f"Backed up {path}")

            with open(path, "r") as f:
                lines = f.readlines()

            settings = {
                "minlen": str(length),
                "minclass": "1",
                "dictcheck": "0",
                "usercheck": "0",
                "maxrepeat": "0",
                "maxsequence": "0"
            }

            new_lines = []
            seen_keys = set()

            for line in lines:
                key_match = re.match(r"^(\w+)\s*=", line.strip())
                if key_match:
                    key = key_match.group(1)
                    if key in settings:
                        new_lines.append(f"{key} = {settings[key]}\n")
                        seen_keys.add(key)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)

            for key, val in settings.items():
                if key not in seen_keys:
                    new_lines.append(f"{key} = {val}\n")

            with open(path, "w") as f:
                f.writelines(new_lines)

            logger.info("Updated pwquality.conf")
            return "Password configuration updated successfully (pwquality)."
        except Exception as e:
            logger.error(f"Failed to update pwquality.conf: {e}")
            return f"Error: {e}"

    def _update_pam_unix(self, length):
        file_path = "/etc/pam.d/common-password"
        backup_path = "/etc/pam.d/common-password.bak"

        if not os.path.exists(file_path):
            return f"File {file_path} not found."

        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backed up {file_path}")

            with open(file_path, "r") as f:
                content = f.read()

            lines = content.splitlines()
            new_lines = []
            replaced = False

            for line in lines:
                if "pam_unix.so" in line and not line.strip().startswith("#"):
                    if "minlen=" in line:
                        new_line = re.sub(r"minlen=\d+", f"minlen={length}", line)
                    else:
                        new_line = f"{line} minlen={length}"

                    new_lines.append(new_line)
                    replaced = True
                else:
                    new_lines.append(line)

            if not replaced:
                logger.warning("pam_unix.so not found in common-password")
                return "pam_unix.so not found in configuration file."

            with open(file_path, "w") as f:
                f.write("\n".join(new_lines) + "\n")

            logger.info("Password configuration updated (pam_unix).")
            return "Password configuration updated successfully (pam_unix)."

        except Exception as e:
            logger.error(f"Failed to update password configuration: {e}")
            if os.path.exists(backup_path):
                logger.info("Restoring backup...")
                shutil.copy2(backup_path, file_path)
            return f"Error: {e}"
