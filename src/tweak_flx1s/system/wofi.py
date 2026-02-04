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
import filecmp
from loguru import logger
from tweak_flx1s.const import HOME_DIR

class WofiManager:
    """Manages Wofi configuration."""

    def __init__(self):
        self.WOFI_CONFIG_DIR = os.path.join(HOME_DIR, ".config/wofi")
        self.APP_CONFIG_DIR = "/usr/share/tweak-flx1s/configs/wofi"
        if not os.path.exists(self.APP_CONFIG_DIR):
             self.APP_CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/configs/wofi"))

    def ensure_config_exists(self):
        """Ensures that Wofi config files exist."""
        if not os.path.exists(self.WOFI_CONFIG_DIR):
            os.makedirs(self.WOFI_CONFIG_DIR)

        for f in ["config", "style.css"]:
            target = os.path.join(self.WOFI_CONFIG_DIR, f)
            if not os.path.exists(target):
                src = os.path.join(self.APP_CONFIG_DIR, f)
                if os.path.exists(src):
                    try:
                        shutil.copy(src, target)
                        logger.info(f"Installed Wofi {f}")
                    except Exception as e:
                        logger.error(f"Failed to copy Wofi {f}: {e}")
                else:
                    logger.warning(f"Source Wofi config not found: {src}")

    def check_config_match(self):
        """Checks if current Wofi config matches the app default."""
        for f in ["config", "style.css"]:
            target = os.path.join(self.WOFI_CONFIG_DIR, f)
            src = os.path.join(self.APP_CONFIG_DIR, f)

            if not os.path.exists(target):
                return False
            if not os.path.exists(src):
                return False

            try:
                if not filecmp.cmp(src, target, shallow=False):
                    return False
            except Exception:
                return False
        return True

    def force_install_config(self):
        """Overwrites Wofi config with app defaults."""
        if not os.path.exists(self.WOFI_CONFIG_DIR):
            os.makedirs(self.WOFI_CONFIG_DIR)

        for f in ["config", "style.css"]:
            src = os.path.join(self.APP_CONFIG_DIR, f)
            target = os.path.join(self.WOFI_CONFIG_DIR, f)

            if os.path.exists(src):
                try:
                    shutil.copy(src, target)
                    logger.info(f"Forced install of Wofi {f}")
                except Exception as e:
                    logger.error(f"Failed to force copy Wofi {f}: {e}")
            else:
                logger.warning(f"Source Wofi config not found: {src}")
