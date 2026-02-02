import os
import json
from tweak_flx1s.const import CONFIG_DIR
from tweak_flx1s.utils import logger
from tweak_flx1s.actions.executor import is_locked, execute_command, show_wofi_menu

CONFIG_FILE = os.path.join(CONFIG_DIR, "gestures.json")

DEFAULT_CONFIG = {
    "gestures": [
        {
            "name": "Switch App Next",
            "spec": "1,RL,B,*,R",
            "locked": {"type": "command", "value": ""},
            "unlocked": {"type": "command", "value": "wtype -M alt -P tab -m alt -p tab"}
        },
        {
            "name": "Switch App Prev",
            "spec": "1,LR,B,*,R",
            "locked": {"type": "command", "value": ""},
            "unlocked": {"type": "command", "value": "wtype -M alt -M shift -P tab -m alt -m shift -p tab"}
        },
        {
            "name": "Kill App",
            "spec": "1,LR,L,L,R",
            "locked": {"type": "command", "value": ""},
            "unlocked": {"type": "command", "value": "wtype -M alt -P F4 -m alt -p F4"}
        },
        {
            "name": "Back",
            "spec": "1,LR,L,S,R",
            "locked": {"type": "command", "value": ""},
            "unlocked": {"type": "command", "value": "wtype -k XF86Back"}
        }
    ]
}

class GesturesManager:
    def __init__(self):
        self.config = self._load_config()

    def _load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return DEFAULT_CONFIG
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                if "gestures" not in data:
                     return DEFAULT_CONFIG
                return data
        except Exception as e:
            logger.error(f"Failed to load gestures config: {e}")
            return DEFAULT_CONFIG

    def save_config(self, new_config=None):
        if new_config:
            self.config = new_config
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

    def handle_gesture(self, index):
        try:
            index = int(index)
        except ValueError:
            logger.error(f"Invalid gesture index: {index}")
            return

        gestures = self.config.get("gestures", [])
        if index < 0 or index >= len(gestures):
            logger.error(f"Gesture index out of range: {index}")
            return

        gesture = gestures[index]
        logger.info(f"Triggering gesture: {gesture.get('name', 'Unknown')}")

        locked = is_locked()
        state_key = "locked" if locked else "unlocked"

        action_config = gesture.get(state_key)
        if not action_config:
             logger.warning(f"No action configured for gesture {index} in {state_key} state.")
             return

        action_type = action_config.get("type")
        if action_type == "command":
            cmd = action_config.get("value")
            execute_command(cmd)
        elif action_type == "wofi":
            items = action_config.get("items", [])
            show_wofi_menu(items)
