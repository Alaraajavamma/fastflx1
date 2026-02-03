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
from tweak_flx1s.utils import run_command
from tweak_flx1s.const import HOME_DIR

class KeyboardManager:
    """Manages keyboard layouts and OSK selection."""

    def __init__(self):
        self.SQUEEKBOARD_DIR = os.path.join(HOME_DIR, ".local/share/squeekboard")
        self.APP_SHARE_DIR = "/usr/share/tweak-flx1s"
        if not os.path.exists(self.APP_SHARE_DIR):
             self.APP_SHARE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../share"))

    def check_squeekboard_installed(self):
        """Checks if squeekboard package is installed."""
        try:
            # Check dpkg first
            res = run_command("dpkg -l squeekboard", check=False)
            if res and "ii  squeekboard" in res:
                 return True
            # Fallback to binary check
            if shutil.which("squeekboard"):
                 return True
            return False
        except Exception as e:
            logger.error(f"Failed to check squeekboard installation: {e}")
            return False

    def get_current_keyboard(self):
        """Returns the currently selected keyboard alternative."""
        try:
            out = run_command("update-alternatives --query phosh-osk", check=False)
            if not out:
                 return "unknown"

            for line in out.splitlines():
                if line.startswith("Value:"):
                    path = line.split(":", 1)[1].strip()
                    if "squeekboard" in path: return "squeekboard"
                    if "stub" in path: return "phosh-osk-stub"
                    if "stevia" in path: return "phosh-osk-stevia"
                    return path
            return "unknown"
        except Exception as e:
            logger.error(f"Failed to get current keyboard: {e}")
            return "unknown"

    def get_available_keyboards(self):
        """
        Returns a list of available keyboard alternatives.
        """
        options = []
        try:
            # Try query first as it might give more info
            logger.info("Querying available keyboards...")
            out = run_command("update-alternatives --query phosh-osk", check=False)
            if out:
                for line in out.splitlines():
                    if line.startswith("Alternative:"):
                        p = line.split(":", 1)[1].strip()
                        name = "Unknown"
                        if "squeekboard" in p: name = "Squeekboard"
                        elif "stub" in p: name = "Phosh OSK (Stub)"
                        elif "stevia" in p: name = "Phosh OSK (Stevia)"
                        else: name = p
                        options.append({"name": name, "path": p})

            # If query failed or empty, try list
            if not options:
                 logger.info("Query returned no results, trying list...")
                 out = run_command("update-alternatives --list phosh-osk", check=False)
                 if out:
                    paths = out.splitlines()
                    for p in paths:
                        name = "Unknown"
                        if "squeekboard" in p: name = "Squeekboard"
                        elif "stub" in p: name = "Phosh OSK (Stub)"
                        elif "stevia" in p: name = "Phosh OSK (Stevia)"
                        else: name = p
                        options.append({"name": name, "path": p})

            logger.info(f"Found {len(options)} keyboards.")

        except Exception as e:
            logger.error(f"Failed to list keyboards: {e}")

        return options

    def set_keyboard(self, path):
        """Returns the command to set the keyboard."""
        logger.info(f"Setting keyboard to {path}")
        return f"update-alternatives --set phosh-osk {path}"

    def install_finnish_layout(self):
        """Copies the custom Finnish layout to ~/.local/share/squeekboard."""
        try:
            src = os.path.join(self.APP_SHARE_DIR, "squeekboard")
            if not os.path.exists(src):
                logger.error(f"Source squeekboard dir not found at {src}")
                return False

            if os.path.exists(self.SQUEEKBOARD_DIR):
                shutil.rmtree(self.SQUEEKBOARD_DIR)

            shutil.copytree(src, self.SQUEEKBOARD_DIR)
            logger.info(f"Installed Finnish layout to {self.SQUEEKBOARD_DIR}")
            return True
        except Exception as e:
            logger.error(f"Failed to install Finnish layout: {e}")
            return False

    def is_finnish_layout_installed(self):
        """Checks if Finnish layout is installed."""
        try:
            check_path = os.path.join(self.SQUEEKBOARD_DIR, "keyboards", "fi.yaml")
            return os.path.exists(check_path)
        except Exception as e:
            logger.error(f"Failed to check Finnish layout: {e}")
            return False

    def remove_finnish_layout(self):
        """Removes the custom layout folder."""
        try:
            if os.path.exists(self.SQUEEKBOARD_DIR):
                shutil.rmtree(self.SQUEEKBOARD_DIR)
                logger.info("Removed Finnish layout")
            return True
        except Exception as e:
             logger.error(f"Failed to remove Finnish layout: {e}")
             return False
