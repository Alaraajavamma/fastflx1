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

import sys
import shutil
import subprocess
import gi

gi.require_version('Gio', '2.0')
from gi.repository import Gio
from loguru import logger
from tweak_flx1s.const import APP_ID

def setup_logging(debug=False):
    """Initializes logging configuration."""
    logger.remove()
    if debug:
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.add(sys.stderr, level="INFO")

def run_command(command, check=True):
    """
    Runs a shell command and returns the output.
    'command' can be a string (shell=True) or a list (shell=False).
    """
    use_shell = isinstance(command, str)
    cmd_str = command if use_shell else " ".join(command)

    logger.debug(f"Running command: {cmd_str}")
    try:
        result = subprocess.run(
            command,
            shell=use_shell,
            check=check,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {cmd_str}")
        logger.error(f"Error output: {e.stderr}")
        if check:
            raise
        return None

def check_dependency(name):
    """Checks if a command line tool exists."""
    return shutil.which(name) is not None

def get_device_model():
    """
    Returns the device model based on 'uname -n'.
    Expected values: 'FuriPhoneFLX1', 'FuriPhoneFLX1s', or 'Unknown'.
    """
    try:
        model = run_command("uname -n", check=False)
        if model in ["FuriPhoneFLX1", "FuriPhoneFLX1s"]:
            return model
        return "Unknown"
    except Exception as e:
        logger.error(f"Failed to detect device model: {e}")
        return "Unknown"

def send_notification(title, body="", icon_name="dialog-information", id=None):
    """
    Sends a notification using Gio.Application.
    """
    try:
        app = Gio.Application(application_id=APP_ID, flags=Gio.ApplicationFlags.NON_UNIQUE)
        app.register(None)

        notification = Gio.Notification.new(title)
        if body:
            notification.set_body(body)
        if icon_name:
            icon = Gio.ThemedIcon.new(icon_name)
            notification.set_icon(icon)

        app.send_notification(id, notification)
        logger.info(f"Notification sent: {title}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
