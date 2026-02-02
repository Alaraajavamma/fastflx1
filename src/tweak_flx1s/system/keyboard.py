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
import os

class KeyboardManager:
    """Manages virtual keyboard selection (Phosh-OSK vs Squeekboard)."""

    def check_squeekboard_installed(self):
        """Checks if squeekboard package is installed."""
        try:
            subprocess.check_call(["dpkg", "-s", "squeekboard"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except:
            return False

    def install_squeekboard(self):
        """Returns command to install squeekboard."""
        return "apt install squeekboard -y"

    def get_current_keyboard(self):
        """Determines currently active virtual keyboard."""
        try:
            out = subprocess.check_output(["update-alternatives", "--display", "Phosh-OSK"], text=True)

            for line in out.splitlines():
                 if line.startswith(" link currently points to"):
                     path = line.split("to ")[-1].strip()
                     if "Squeekboard" in path:
                         return "squeekboard"
                     elif "Phosh.OskStub" in path:
                         return "phosh-osk"
            return "unknown"
        except:
            return "unknown"

    def set_keyboard(self, keyboard_type):
        """Returns command to set virtual keyboard."""
        path = ""
        if keyboard_type == "squeekboard":
             path = "/usr/share/applications/sm.puri.Squeekboard.desktop"
        elif keyboard_type == "phosh-osk":
             path = "/usr/share/phosh-osk-stub/sm.puri.Phosh.OskStub.desktop"

        if path:
            return f"update-alternatives --set Phosh-OSK {path}"
        return ""
