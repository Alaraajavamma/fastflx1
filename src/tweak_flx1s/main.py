"""
Main entry point for Tweak-FLX1s.
Copyright (C) 2024 Alaraajavamma <aki@urheiluaki.fi>
License: GPL-3.0-or-later
"""

import sys
import argparse
from tweak_flx1s.utils import setup_logging

def main():
    """Parses arguments and dispatches actions."""
    setup_logging()

    parser = argparse.ArgumentParser(description="Tweak-FLX1s")
    parser.add_argument("--monitor", help="Start a monitor service")
    parser.add_argument("--action", help="Perform a one-off action")
    parser.add_argument("--user", help="Specify target user (for system services)")
    parser.add_argument("--trigger-gesture", help="Trigger a configured gesture by index")

    parser.add_argument("--short-press", action="store_true", help="Handle short press event")
    parser.add_argument("--double-press", action="store_true", help="Handle double press event")
    parser.add_argument("--long-press", action="store_true", help="Handle long press event")

    args, unknown = parser.parse_known_args()

    if args.trigger_gesture is not None:
        from tweak_flx1s.actions.gestures import GesturesManager
        GesturesManager().handle_gesture(args.trigger_gesture)
        return

    if args.short_press:
        from tweak_flx1s.actions.buttons import ButtonManager
        ButtonManager().handle_press("short_press")
        return

    if args.double_press:
        from tweak_flx1s.actions.buttons import ButtonManager
        ButtonManager().handle_press("double_press")
        return

    if args.long_press:
        from tweak_flx1s.actions.buttons import ButtonManager
        ButtonManager().handle_press("long_press")
        return

    if args.monitor:
        if args.monitor == "alarm":
             from tweak_flx1s.services.alarm import run
             run()
        elif args.monitor == "guard":
             from tweak_flx1s.services.guard import run
             run()
        elif args.monitor == "gestures":
             from tweak_flx1s.services.gestures import run
             run()
        elif args.monitor == "andromeda-fs":
             from tweak_flx1s.system.andromeda import AndromedaManager
             mgr = AndromedaManager()
             if args.user:
                 mgr.HOST_USER = args.user
                 mgr.HOST_HOME = f"/home/{args.user}"
                 mgr._reinit_paths()
             mgr.watch()
        return

    if args.action:
         from tweak_flx1s.actions.shortcuts import ShortcutsManager
         mgr = ShortcutsManager()
         if args.action == "screenshot":
             mgr.take_screenshot()
         elif args.action == "flashlight":
             mgr.toggle_flashlight()
         elif args.action == "kill-window":
             mgr.kill_active_window()
         elif args.action == "paste":
             mgr.paste_clipboard()
         return

    from tweak_flx1s.gui.app import start_gui
    sys.exit(start_gui())

if __name__ == "__main__":
    main()
