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

from tweak_flx1s.utils import logger, run_command

class DebUiManager:
    """Manages DebUI package installation and removal."""

    def check_installed(self):
        """Checks if deb-ui is installed."""
        # Try checking 'deb-ui' first (standard naming)
        try:
             run_command("dpkg -s deb-ui", check=True)
             return True
        except Exception:
             pass

        # Try 'debui'
        try:
             run_command("dpkg -s debui", check=True)
             return True
        except Exception:
             return False

    def get_install_cmd(self):
        """Returns command to install DebUI."""
        # Clone to /tmp and install.
        # We assume git is available (installed dependency).
        return (
            "rm -rf /tmp/debui && "
            "git clone https://gitlab.com/Alaraajavamma/debui /tmp/debui && "
            "cd /tmp/debui && "
            "apt install -y ./debui*.deb"
        )

    def get_remove_cmd(self):
        """Returns command to remove DebUI."""
        # We try to remove both potential package names to be safe,
        # ignoring errors if one doesn't exist.
        return "apt remove -y deb-ui debui"
