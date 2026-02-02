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
    try:
        subprocess.check_call(["pgrep", "-x", "wofi"], stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def execute_command(cmd):
    if cmd:
        logger.info(f"Executing command: {cmd}")
        subprocess.Popen(cmd, shell=True)

def show_wofi_menu(items):
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
