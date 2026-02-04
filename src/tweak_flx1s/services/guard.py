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

import signal
import threading
import subprocess
from gi.repository import Gio, GLib
from loguru import logger
from tweak_flx1s.utils import run_command
from tweak_flx1s.const import APP_ID

class AndromedaGuardService:
    """
    Python implementation of the Andromeda Guard service.
    Monitors the 'org.gnome.desktop.a11y.applications screen-keyboard-enabled' setting
    and manages notifications with countdowns and cleanup.
    """

    def __init__(self):
        self.app = Gio.Application(application_id=APP_ID, flags=Gio.ApplicationFlags.NON_UNIQUE)
        self.app.register(None)
        self.notification_id = "andromeda-guard-notification"
        self._running = True
        self.loop = None
        self.withdrawal_source_id = None
        self.countdown_source_id = None
        self.counter = 0

    def run(self):
        """Starts the guard service loop."""
        logger.info("Starting Andromeda Guard Service...")

        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, self._quit_service)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, self._quit_service)

        GLib.idle_add(self._perform_reset)

        t = threading.Thread(target=self._monitor_dbus, daemon=True)
        t.start()

        self.loop = GLib.MainLoop()
        try:
            self.loop.run()
        except KeyboardInterrupt:
            self._quit_service()

    def _quit_service(self):
        self._running = False
        if self.loop:
            self.loop.quit()
        return GLib.SOURCE_REMOVE

    def _perform_reset(self):
        """Performs the disable -> wait -> enable cycle."""
        logger.info("Performing OSK reset cycle.")
        self._disable_keyboard()
        self._start_countdown(40)
        return False

    def _handle_session_reset(self):
        """Quick reset triggered by session signal."""
        logger.info("Handling session reset signal.")
        GLib.idle_add(self._trigger_session_reset_ui)

    def _trigger_session_reset_ui(self):
        self._disable_keyboard()
        self._start_countdown(20)
        return False

    def _disable_keyboard(self):
        run_command("gsettings set org.gnome.desktop.a11y.applications screen-keyboard-enabled false", check=False)

    def _enable_keyboard(self):
        run_command("gsettings set org.gnome.desktop.a11y.applications screen-keyboard-enabled true", check=False)
        self._send_notification("Andromeda is ready - OSK Unlocked", expire_timeout=3000)

    def _start_countdown(self, seconds):
        self.counter = seconds
        if self.countdown_source_id is None:
             self.countdown_source_id = GLib.timeout_add_seconds(1, self._on_tick)

        self._update_notification()

    def _on_tick(self):
        if not self._running:
             self.countdown_source_id = None
             return False

        self.counter -= 1
        if self.counter <= 0:
             self._enable_keyboard()
             self.countdown_source_id = None
             return False

        self._update_notification()
        return True

    def _update_notification(self):
        """Update notification every 5 seconds."""
        if self.counter % 5 == 0:
            expire_ms = self.counter * 1000 + 1000
            msg = f"OSK locked for {self.counter} seconds"
            self._send_notification(msg, expire_timeout=expire_ms)

    def _send_notification(self, body, expire_timeout=None):
        """Sends a notification using Gio and manages withdrawal."""
        if self.withdrawal_source_id:
            GLib.source_remove(self.withdrawal_source_id)
            self.withdrawal_source_id = None

        notification = Gio.Notification.new("Andromeda display guard")
        notification.set_body(body)
        notification.set_icon(Gio.ThemedIcon.new("input-keyboard"))

        self.app.send_notification(self.notification_id, notification)

        if expire_timeout:
             self.withdrawal_source_id = GLib.timeout_add(expire_timeout, self._withdraw)

    def _withdraw(self):
        self.app.withdraw_notification(self.notification_id)
        self.withdrawal_source_id = None
        return False

    def _monitor_dbus(self):
        """Monitors DBus for the custom signal."""
        cmd = ["dbus-monitor", "--session", "type='signal',interface='org.freedesktop.DBus',member='NameAcquired'"]
        logger.debug(f"Running dbus monitor: {' '.join(cmd)}")
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

            while self._running:
                line = process.stdout.readline()
                if not line:
                    break
                if "io.furios.Andromeda.Session" in line:
                    self._handle_session_reset()
        except Exception as e:
            logger.error(f"Error in DBus monitor: {e}")
        finally:
            if 'process' in locals() and process:
                process.terminate()

def run():
    service = AndromedaGuardService()
    service.run()
