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

class BatMonManager:
    """Manages FLX1s-Bat-Mon package installation and removal."""

    def check_installed(self):
        """Checks if flx1s-bat-mon is installed."""
        try:
             run_command("dpkg -s flx1s-bat-mon", check=True)
             return True
        except Exception:
             return False

    def get_install_cmd(self):
        """Returns command to install FLX1s-Bat-Mon."""
        return (
            "rm -rf /tmp/flx1s-bat-mon && "
            "git clone https://gitlab.com/Alaraajavamma/flx1s-bat-mon /tmp/flx1s-bat-mon && "
            "cd /tmp/flx1s-bat-mon && "
            "apt install -y ./flx1s-bat-mon*.deb"
        )

    def get_remove_cmd(self):
        """Returns command to remove FLX1s-Bat-Mon."""
        return "apt remove -y flx1s-bat-mon"
