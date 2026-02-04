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
from tweak_flx1s.utils import logger, run_command

class PhofonoManager:
    """Manages Phofono package installation and removal."""

    def check_installed(self):
        """Checks if phofono is installed."""
        try:
             logger.debug("Checking if phofono is installed...")
             run_command("dpkg -s phofono", check=True)
             return True
        except Exception:
             return False

    def prepare_install(self):
        """Prepares environment for phofono installation."""
        logger.info("Preparing install: stopping services...")
        run_command("systemctl --user stop calls-daemon", check=False)
        run_command("systemctl --user mask calls-daemon", check=False)

        work_dir = "/tmp/phofono"
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)

        logger.info("Cloning phofono repo...")
        cmd = f"git clone https://gitlab.com/Alaraajavamma/phofono {work_dir}"
        run_command(cmd)

        return work_dir

    def get_install_root_cmd(self, repo_dir):
        """Returns root script for installation."""
        script = f"""
set -e
cd "{repo_dir}"
echo "Installing package..."
apt install -y ./phofono_*.deb

echo "Configuring diversions..."
dpkg-divert --add --rename --divert /etc/xdg/autostart/sm.puri.Chatty-daemon.desktop.disabled /etc/xdg/autostart/sm.puri.Chatty-daemon.desktop || true
dpkg-divert --add --rename --divert /etc/xdg/autostart/org.gnome.Calls-daemon.desktop.disabled /etc/xdg/autostart/org.gnome.Calls-daemon.desktop || true
dpkg-divert --add --rename --divert /usr/share/applications/sm.puri.Chatty.desktop.disabled /usr/share/applications/sm.puri.Chatty.desktop || true
dpkg-divert --add --rename --divert /usr/share/applications/org.gnome.Calls.desktop.disabled /usr/share/applications/org.gnome.Calls.desktop || true

echo "Root tasks complete."
"""
        return script

    def finish_install(self):
        """Finalizes installation as user."""
        logger.info("Finishing install: configuring user services...")
        dbus_dir = os.path.expanduser("~/.local/share/dbus-1/services/")
        os.makedirs(dbus_dir, exist_ok=True)
        service_file = os.path.join(dbus_dir, "org.gnome.Calls.service")
        with open(service_file, "w") as f:
            f.write("[D-BUS Service]\nName=org.gnome.Calls\nExec=/bin/true")

        run_command("systemctl --user disable ofono-toned", check=False)
        run_command("systemctl --user mask ofono-toned", check=False)
        run_command("pkill -f ofono-toned", check=False)

        work_dir = "/tmp/phofono"
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)

    def get_uninstall_root_cmd(self):
        """Returns root script for uninstallation."""
        script = """
set -e
echo "Removing package..."
apt remove -y phofono

echo "Removing diversions..."
dpkg-divert --remove --rename /etc/xdg/autostart/sm.puri.Chatty-daemon.desktop || true
dpkg-divert --remove --rename /etc/xdg/autostart/org.gnome.Calls-daemon.desktop || true
dpkg-divert --remove --rename /usr/share/applications/sm.puri.Chatty.desktop || true
dpkg-divert --remove --rename /usr/share/applications/org.gnome.Calls.desktop || true

echo "Root tasks complete."
"""
        return script

    def finish_uninstall(self):
        """Finalizes uninstallation as user."""
        logger.info("Finishing uninstall: restoring user services...")
        run_command("systemctl --user unmask calls-daemon", check=False)

        dbus_file = os.path.expanduser("~/.local/share/dbus-1/services/org.gnome.Calls.service")
        if os.path.exists(dbus_file):
            os.remove(dbus_file)

        run_command("systemctl --user daemon-reload", check=False)

        run_command("systemctl --user unmask ofono-toned", check=False)
        run_command("systemctl --user enable ofono-toned", check=False)
        run_command("systemctl --user start ofono-toned", check=False)
