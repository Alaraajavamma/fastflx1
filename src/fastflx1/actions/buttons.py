import os
import json
import subprocess
from gi.repository import GLib
from fastflx1.utils import logger, run_command

CONFIG_FILE = os.path.expanduser("~/.config/fastflx1/buttons.json")

DEFAULT_CONFIG = {
    "short_press": {
        "locked": {"type": "command", "value": "fastflx1 --action flashlight"},
        "unlocked": {"type": "wofi", "items": [
            {"label": "Flashlight", "cmd": "fastflx1 --action flashlight"},
            {"label": "Screenshot", "cmd": "fastflx1 --action screenshot"},
            {"label": "Kill Active Window", "cmd": "fastflx1 --action kill-window"}
        ]}
    },
    "double_press": {
        "locked": {"type": "command", "value": ""},
        "unlocked": {"type": "command", "value": ""}
    },
    "long_press": {
        "locked": {"type": "command", "value": ""},
        "unlocked": {"type": "command", "value": ""}
    }
}

class ButtonManager:
    def __init__(self):
        self.config = self._load_config()

    def _load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return DEFAULT_CONFIG
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load button config: {e}")
            return DEFAULT_CONFIG

    def save_config(self, new_config=None):
        if new_config:
            self.config = new_config
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

    def is_locked(self):
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

    def is_wofi_running(self):
        try:
            subprocess.check_call(["pgrep", "-x", "wofi"], stdout=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    def handle_press(self, press_type):
        """
        Handle a button press event.
        press_type: 'short_press', 'double_press', 'long_press'
        """
        logger.info(f"Handling button press: {press_type}")

        if press_type == "short_press" and self.is_wofi_running():
            logger.info("Wofi is running, simulating Enter key.")
            run_command("wtype -k Return", check=False)
            return

        locked = self.is_locked()
        state_key = "locked" if locked else "unlocked"
        logger.info(f"System locked: {locked}")

        action_config = self.config.get(press_type, {}).get(state_key)
        if not action_config:
            logger.warning(f"No action configured for {press_type} in {state_key} state.")
            return

        action_type = action_config.get("type")

        if action_type == "command":
            cmd = action_config.get("value")
            if cmd:
                logger.info(f"Executing command: {cmd}")
                subprocess.Popen(cmd, shell=True)

        elif action_type == "wofi":
            items = action_config.get("items", [])
            self._show_wofi_menu(items)

    def _show_wofi_menu(self, items):
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
                subprocess.Popen(cmd, shell=True)
            else:
                logger.warning("Invalid selection")

        except Exception as e:
            logger.error(f"Error running wofi: {e}")
