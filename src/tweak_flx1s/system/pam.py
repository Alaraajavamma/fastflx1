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

    def get_min_password_length(self):
        """Reads current minimum password length from /etc/pam.d/common-password."""
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
        Updates /etc/pam.d/common-password to set minimum password length.
        """
        logger.info(f"Setting minimum password length to {length}...")

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

            logger.info("Password configuration updated.")
            return "Password configuration updated successfully."

        except Exception as e:
            logger.error(f"Failed to update password configuration: {e}")
            if os.path.exists(backup_path):
                logger.info("Restoring backup...")
                shutil.copy2(backup_path, file_path)
            return f"Error: {e}"
