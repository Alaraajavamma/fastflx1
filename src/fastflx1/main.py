import sys
import argparse
from fastflx1.utils import setup_logging, logger

def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="FastFLX1")
    parser.add_argument("--monitor", help="Start a monitor service")
    parser.add_argument("--action", help="Perform a one-off action")
    parser.add_argument("--user", help="Specify target user (for system services)")

    # Button event handlers
    parser.add_argument("--short-press", action="store_true", help="Handle short press event")
    parser.add_argument("--double-press", action="store_true", help="Handle double press event")
    parser.add_argument("--long-press", action="store_true", help="Handle long press event")

    args, unknown = parser.parse_known_args()

    if args.short_press:
        from fastflx1.actions.buttons import ButtonManager
        ButtonManager().handle_press("short_press")
        return

    if args.double_press:
        from fastflx1.actions.buttons import ButtonManager
        ButtonManager().handle_press("double_press")
        return

    if args.long_press:
        from fastflx1.actions.buttons import ButtonManager
        ButtonManager().handle_press("long_press")
        return

    if args.monitor:
        if args.monitor == "alarm":
             from fastflx1.services.alarm import run
             run()
        elif args.monitor == "guard":
             from fastflx1.services.guard import run
             run()
        elif args.monitor == "gestures":
             from fastflx1.services.gestures import run
             run()
        elif args.monitor == "andromeda-fs":
             # This runs as root usually
             from fastflx1.system.andromeda import AndromedaManager
             mgr = AndromedaManager()
             if args.user:
                 mgr.HOST_USER = args.user
                 mgr.HOST_HOME = f"/home/{args.user}" # Fallback
                 # Better to re-init paths based on new user
                 mgr._reinit_paths()
             mgr.watch()
        return

    if args.action:
         from fastflx1.actions.shortcuts import ShortcutsManager
         mgr = ShortcutsManager()
         if args.action == "screenshot":
             mgr.take_screenshot()
         elif args.action == "flashlight":
             mgr.toggle_flashlight()
         elif args.action == "kill-window":
             mgr.kill_active_window()
         return

    # Default: Start GUI
    from fastflx1.gui.app import start_gui
    sys.exit(start_gui())

if __name__ == "__main__":
    main()
