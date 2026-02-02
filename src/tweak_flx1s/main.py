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
import argparse
from tweak_flx1s.utils import setup_logging
from tweak_flx1s.core.i18n import install_i18n

def main():
    """Parses arguments and dispatches actions."""
    install_i18n()

    parser = argparse.ArgumentParser(description="Tweak-FLX1s")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--monitor", help="Start a monitor service")
    parser.add_argument("--action", help="Perform a one-off action")
    parser.add_argument("--user", help="Specify target user (for system services)")
    parser.add_argument("--trigger-gesture", help="Trigger a configured gesture by index")

    parser.add_argument("--short-press", action="store_true", help="Handle short press event")
    parser.add_argument("--double-press", action="store_true", help="Handle double press event")
    parser.add_argument("--long-press", action="store_true", help="Handle long press event")

    args, unknown = parser.parse_known_args()
    setup_logging(debug=args.debug)

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
