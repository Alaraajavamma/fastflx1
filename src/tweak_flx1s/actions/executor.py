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
import subprocess
from tweak_flx1s.utils import logger, run_command

def is_locked():
    """Check session lock status using loginctl."""
    try:
        user = os.environ.get('USER')
        if not user:
            return False

        out = run_command(f"loginctl list-sessions --no-legend", check=False)
        session_id = None
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[2] == user:
                session_id = parts[0]
                break

        if not session_id:
            return False

        out = run_command(f"loginctl show-session {session_id} -p LockedHint", check=False)
        return "LockedHint=yes" in out
    except Exception as e:
        logger.error(f"Error checking lock state: {e}")
        return False

def is_wofi_running():
    """Checks if wofi is currently running."""
    try:
        subprocess.check_call(["pgrep", "-x", "wofi"], stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def execute_command(cmd):
    """Executes a shell command in background."""
    if cmd:
        logger.info(f"Executing command: {cmd}")
        subprocess.Popen(cmd, shell=True)

def show_wofi_menu(items):
    """Shows a wofi menu with given items."""
    if len(items) > 7:
        logger.warning("Too many items for Wofi menu, truncating to 7.")
        items = items[:7]

    wofi_input = ""
    cmd_map = {}

    for idx, item in enumerate(items, 1):
        label = item.get("label", "Unknown")
        cmd = item.get("cmd", "")
        display_str = f"{idx}. {label}"
        wofi_input += f"{display_str}\n"
        cmd_map[display_str] = cmd

    close_idx = len(items) + 1
    display_close = f"{close_idx}. Close"
    wofi_input += display_close

    logger.info("Opening Wofi menu")
    try:
        process = subprocess.Popen(
            ["wofi", "-d", "--prompt", "Select an option:", "--lines", str(close_idx)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=wofi_input)

        selection = stdout.strip()
        logger.info(f"User selected: {selection}")

        if selection == display_close:
            return

        if selection in cmd_map:
            cmd = cmd_map[selection]
            logger.info(f"Executing menu command: {cmd}")
            execute_command(cmd)
        else:
            logger.warning("Invalid selection")

    except Exception as e:
        logger.error(f"Error running wofi: {e}")
