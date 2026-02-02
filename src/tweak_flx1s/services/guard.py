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
import time
from gi.repository import GLib, Gio
from tweak_flx1s.utils import logger, send_notification

class AndromedaGuard:
    def __init__(self):
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.loop = GLib.MainLoop()
        self.settings = Gio.Settings.new("org.gnome.desktop.a11y.applications")

    def notify_with_countdown(self, seconds):
        """Sends a countdown notification updating every 5 seconds."""
        for i in range(seconds, 0, -1):
            if i % 5 == 0 or i == seconds:
                send_notification(
                    "Andromeda Guard",
                    f"OSK locked for {i} seconds",
                    icon_name="input-keyboard",
                    id="andromeda-guard"
                )
            time.sleep(1)

    def enable_keyboard(self):
        """Enables the on-screen keyboard and notifies the user."""
        self.settings.set_boolean("screen-keyboard-enabled", True)
        send_notification(
            "Andromeda Guard",
            "Andromeda is ready - OSK Unlocked",
            icon_name="input-keyboard",
            id="andromeda-guard"
        )
        logger.info("OSK Enabled")

    def disable_keyboard(self):
        """Disables the on-screen keyboard."""
        self.settings.set_boolean("screen-keyboard-enabled", False)
        logger.info("OSK Disabled")

    def handle_session_reset(self):
        """Handles the Andromeda session reset event."""
        logger.info("Handling session reset")
        self.disable_keyboard()
        self.notify_with_countdown(20)
        self.enable_keyboard()

    def initial_setup(self):
        """Performs initial setup and countdown."""
        logger.info("Running initial setup")
        self.disable_keyboard()
        self.notify_with_countdown(40)
        self.enable_keyboard()

    def on_name_acquired(self, connection, sender_name, object_path, interface_name, signal_name, parameters, user_data):
        """Callback for DBus NameAcquired signal."""
        name = parameters.unpack()[0]
        if name == "io.furios.Andromeda.Session":
            logger.info(f"Detected NameAcquired: {name}")
            self.handle_session_reset()

    def start(self):
        """Starts the guard service."""
        self.initial_setup()

        self.bus.signal_subscribe(
            "org.freedesktop.DBus",
            "org.freedesktop.DBus",
            "NameAcquired",
            "/org/freedesktop/DBus",
            None,
            Gio.DBusSignalFlags.NONE,
            self.on_name_acquired,
            None
        )

        logger.info("Monitoring for Andromeda Session...")
        try:
            self.loop.run()
        except KeyboardInterrupt:
            pass

def run():
    guard = AndromedaGuard()
    guard.start()

if __name__ == "__main__":
    from tweak_flx1s.utils import setup_logging
    setup_logging()
    run()
