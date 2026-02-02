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

import time
import subprocess
import threading
from gi.repository import Gio, GLib
from tweak_flx1s.utils import logger, run_command

class AndromedaGuardService:
    """
    Python implementation of the Andromeda Guard service.
    Monitors the 'org.gnome.desktop.a11y.applications screen-keyboard-enabled' setting
    and manages notifications with countdowns and cleanup.
    """

    def __init__(self):
        self.app = Gio.Application(application_id="io.FuriOS.Andromeda.Guard", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.app.register(None)
        self.notification_id = "andromeda-guard-notification"
        self._running = True

    def run(self):
        """Starts the guard service loop."""
        logger.info("Starting Andromeda Guard Service...")

        # Initial Reset
        self._perform_reset()

        # Start DBus Monitor in a thread
        t = threading.Thread(target=self._monitor_dbus, daemon=True)
        t.start()

        # Keep main thread alive
        loop = GLib.MainLoop()
        try:
            loop.run()
        except KeyboardInterrupt:
            self._running = False

    def _perform_reset(self):
        """Performs the disable -> wait -> enable cycle."""
        logger.info("Performing OSK reset cycle.")
        self._disable_keyboard()
        self._countdown_notify(40)
        self._enable_keyboard()

    def _handle_session_reset(self):
        """Quick reset triggered by session signal."""
        logger.info("Handling session reset signal.")
        self._disable_keyboard()
        self._countdown_notify(20)
        self._enable_keyboard()

    def _disable_keyboard(self):
        run_command("gsettings set org.gnome.desktop.a11y.applications screen-keyboard-enabled false", check=False)

    def _enable_keyboard(self):
        run_command("gsettings set org.gnome.desktop.a11y.applications screen-keyboard-enabled true", check=False)
        self._send_notification("Andromeda is ready - OSK Unlocked", expire_timeout=3000)

    def _countdown_notify(self, seconds):
        """Shows a countdown notification."""
        for i in range(seconds, 0, -1):
            if not self._running: break

            if i % 5 == 0 or i == seconds:
                expire_ms = i * 1000
                msg = f"OSK locked for {i} seconds"
                self._send_notification(msg, expire_timeout=expire_ms)

            time.sleep(1)

    def _send_notification(self, body, expire_timeout=None):
        """Sends a notification using Gio."""
        # Note: Gio.Notification doesn't expose expire-time directly in Python bindings easily
        # without GVariant magic or using the backend directly.
        # However, we can use the 'transient' hint via set_priority or low-level API.
        # But to match 'notify-send --expire-time', we might need to withdraw it manually or rely on daemon.

        # Since the user specifically mentioned fading away correctly,
        # and Gio.Notification is persistent by default in Gnome Shell unless configured otherwise,
        # we will simulate the behavior by using GNotification but relying on the shell's expiration if possible,
        # OR we fallback to `notify-send` if strict timing control is needed and Gio is limited.

        # GApplication/GNotification is preferred by the user ("Notifications must be implemented using native...").
        # Standard GNotification doesn't have explicit timeout API exposed easily.
        # However, we can withdraw it after a timeout.

        notification = Gio.Notification.new("Andromeda display guard")
        notification.set_body(body)
        notification.set_icon(Gio.ThemedIcon.new("input-keyboard"))
        # High priority to ensure it shows up? Or Low/Normal?
        # Transient notifications usually are normal.

        self.app.send_notification(self.notification_id, notification)

        if expire_timeout:
             # Schedule withdrawal
             GLib.timeout_add(expire_timeout, lambda: self.app.withdraw_notification(self.notification_id))

    def _monitor_dbus(self):
        """Monitors DBus for the custom signal."""
        # Using subprocess for dbus-monitor as in the original script is robust enough
        cmd = ["dbus-monitor", "--session", "type='signal',interface='org.freedesktop.DBus',member='NameAcquired'"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

        while self._running:
            line = process.stdout.readline()
            if not line: break
            if "io.furios.Andromeda.Session" in line:
                self._handle_session_reset()

def run():
    service = AndromedaGuardService()
    service.run()
