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
import json
from loguru import logger
from tweak_flx1s.utils import run_command
from tweak_flx1s.const import CONFIG_DIR, HOME_DIR
from tweak_flx1s.actions.executor import is_locked, is_wofi_running, execute_command, show_wofi_menu

CONFIG_FILE = os.path.join(CONFIG_DIR, "buttons.json")
ASSISTANT_BUTTON_DIR = os.path.join(HOME_DIR, ".config", "assistant-button")

PREDEFINED_ACTIONS = {
    "Copy (Ctrl+C)": "wtype -M ctrl c -m ctrl",
    "Paste (Ctrl+V)": "wtype -M ctrl v -m ctrl",
    "Cut (Ctrl+X)": "wtype -M ctrl x -m ctrl",
    "Select All & Copy": "wtype -M ctrl a -m ctrl && wtype -M ctrl c -m ctrl",
    "Paste from Clipboard": "tweak-flx1s --action paste",
    "Kill Active Window": "wtype -M alt -P F4 -m alt -p F4",
    "Switch Window": "wtype -M alt -P tab -m alt -p tab",
    "Screenshot": "tweak-flx1s --action screenshot",
    "Flashlight": "tweak-flx1s --action flashlight"
}

DEFAULT_CONFIG = {
    "short_press": {
        "use_custom_file": False,
        "locked": {"type": "command", "value": "tweak-flx1s --action flashlight"},
        "unlocked": {"type": "wofi", "items": [
            {"label": "Flashlight", "cmd": "tweak-flx1s --action flashlight"},
            {"label": "Screenshot", "cmd": "tweak-flx1s --action screenshot"},
            {"label": "Kill Active Window", "cmd": "tweak-flx1s --action kill-window"}
        ]}
    },
    "double_press": {
        "use_custom_file": False,
        "locked": {"type": "command", "value": ""},
        "unlocked": {"type": "command", "value": ""}
    },
    "long_press": {
        "use_custom_file": False,
        "locked": {"type": "command", "value": ""},
        "unlocked": {"type": "command", "value": ""}
    }
}

class ButtonManager:
    """Manages button presses and configuration."""
    def __init__(self):
        self.config = self._load_config()

    def _load_config(self):
        """Loads configuration from JSON file."""
        if not os.path.exists(CONFIG_FILE):
            return DEFAULT_CONFIG
        try:
            with open(CONFIG_FILE, 'r') as f:
                conf = json.load(f)
                return conf
        except Exception as e:
            logger.error(f"Failed to load button config: {e}")
            return DEFAULT_CONFIG

    def save_config(self, new_config=None):
        """Saves configuration to JSON file."""
        if new_config:
            self.config = new_config
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

        self.update_assistant_files()

    def update_assistant_files(self):
        """Generates the ~/.config/assistant-button/* files if enabled."""
        os.makedirs(ASSISTANT_BUTTON_DIR, exist_ok=True)

        press_types = ["short_press", "double_press", "long_press"]
        for ptype in press_types:
            conf = self.config.get(ptype, {})
            if conf.get("use_custom_file", False):
                path = os.path.join(ASSISTANT_BUTTON_DIR, ptype)
                cmd = f"tweak-flx1s --{ptype.replace('_', '-')}"
                try:
                    with open(path, "w") as f:
                        f.write(cmd)
                    logger.info(f"Updated {path} with command: {cmd}")
                except Exception as e:
                    logger.error(f"Failed to write {path}: {e}")

    def handle_press(self, press_type):
        """
        Handle a button press event.
        press_type: 'short_press', 'double_press', 'long_press'
        """
        logger.info(f"Handling button press: {press_type}")

        if press_type == "short_press" and is_wofi_running():
            logger.info("Wofi is running, simulating Enter key.")
            run_command("wtype -k Return", check=False)
            return

        locked = is_locked()
        state_key = "locked" if locked else "unlocked"
        logger.info(f"System locked: {locked}")

        action_config = self.config.get(press_type, {}).get(state_key)
        if not action_config:
            logger.warning(f"No action configured for {press_type} in {state_key} state.")
            return

        action_type = action_config.get("type")

        if action_type == "command":
            cmd = action_config.get("value")
            execute_command(cmd)

        elif action_type == "wofi":
            items = action_config.get("items", [])
            show_wofi_menu(items)
