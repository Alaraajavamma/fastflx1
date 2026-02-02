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

import subprocess
from tweak_flx1s.utils import logger, run_command

class PackageManager:
    """Helper class for package management commands."""

    def switch_to_staging(self):
        """Returns command to switch to staging repositories."""
        cmd = (
            "sudo apt install furios-apt-config-staging furios-apt-config-debian-staging -y && "
            "sudo apt update && "
            "sudo apt install furios-apt-config-krypton-staging -y && "
            "sudo apt update && "
            "sudo apt upgrade -y --allow-downgrades"
        )
        return self._run_in_terminal(cmd)

    def switch_to_production(self):
        """Returns command to switch to production repositories."""
        cmd = (
            "sudo apt remove furios-apt-config-staging furios-apt-config-debian-staging furios-apt-config-krypton-staging -y && "
            "sudo apt update && "
            "sudo apt upgrade -y --allow-downgrades"
        )
        return self._run_in_terminal(cmd)

    def upgrade_system(self):
        """Returns command to upgrade system."""
        cmd = "sudo apt update && sudo apt upgrade -y --allow-downgrades"
        return self._run_in_terminal(cmd)

    def install_branchy(self):
        """Returns command to install furios-app-branchy."""
        cmd = "sudo apt install furios-app-branchy -y"
        return self._run_in_terminal(cmd)

    def _run_in_terminal(self, command):
        """Helper to format command for execution."""
        return command.replace("sudo ", "")
