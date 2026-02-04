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
import signal
import gi
from gi.repository import GLib, Gio
from tweak_flx1s.utils import logger, run_command

class AlarmMonitor:
    """Monitors alarm events to ensure wake-up."""
    def __init__(self):
        self.loop = GLib.MainLoop()
        self.subprocess = None
        self.cancellable = Gio.Cancellable()
        self.data_input_stream = None
        self.lines_to_check = 0

    def start(self):
        """Starts the monitoring process."""
        logger.info("Starting Alarm Monitor")

        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, self._on_quit)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, self._on_quit)

        self._start_monitor_subprocess()

        try:
            self.loop.run()
        except KeyboardInterrupt:
            self._on_quit()

    def _on_quit(self):
        """Handles termination signals."""
        logger.info("Stopping Alarm Monitor...")
        self.cancellable.cancel()

        if self.subprocess:
            self.subprocess.force_exit()

        if self.loop.is_running():
            self.loop.quit()
        return GLib.SOURCE_REMOVE

    def _start_monitor_subprocess(self):
        """
        Runs dbus-monitor to intercept TriggerFeedback method calls.
        This is required because we need to see method calls destined for other services.
        """
        cmd = ["dbus-monitor", "type='method_call',interface='org.sigxcpu.Feedback',member='TriggerFeedback'"]
        logger.debug(f"Running: {' '.join(cmd)}")

        try:
            self.subprocess = Gio.Subprocess.new(
                cmd,
                Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE
            )

            stdout_pipe = self.subprocess.get_stdout_pipe()
            self.data_input_stream = Gio.DataInputStream.new(stdout_pipe)

            self._read_line()

        except Exception as e:
            logger.error(f"Failed to start dbus-monitor: {e}")
            self._on_quit()

    def _read_line(self):
        """Reads a line asynchronously from the subprocess stdout."""
        self.data_input_stream.read_line_async(
            GLib.PRIORITY_DEFAULT,
            self.cancellable,
            self._on_line_read
        )

    def _on_line_read(self, source, result):
        """Callback when a line is read."""
        try:
            line_bytes, length = source.read_line_finish(result)
            if line_bytes is None:
                logger.warning("dbus-monitor stream ended")
                self._on_quit()
                return

            line = line_bytes.decode('utf-8').strip()
            self._process_line(line)
            self._read_line()

        except  GLib.Error as e:
            if e.code != Gio.IOErrorEnum.CANCELLED:
                 logger.error(f"Error reading line: {e}")
                 self._on_quit()

    def _process_line(self, line):
        """Processes a single line from dbus-monitor."""
        if self.lines_to_check > 0:
            self.lines_to_check -= 1
            if "alarm-clock-elapsed" in line:
                self._perform_action()
                self.lines_to_check = 0
                return

        if "org.gnome.clocks" in line:
            self.lines_to_check = 5

    def _perform_action(self):
        """Wakes up the screen and maximizes volume."""
        logger.info("Alarm clock event detected!")

        try:
            if os.path.exists("/sys/class/leds/lcd-backlight/brightness"):
                with open("/sys/class/leds/lcd-backlight/brightness", "r") as f:
                    brightness = int(f.read().strip())

                if brightness == 0:
                    logger.info("Screen is off, waking up/pressing power...")
                    run_command("wtype -P XF86PowerOff", check=False)
        except Exception as e:
            logger.error(f"Error checking brightness: {e}")

        run_command("amixer set Master 100% unmute", check=False)

def run():
    monitor = AlarmMonitor()
    monitor.start()

if __name__ == "__main__":
    from tweak_flx1s.utils import setup_logging
    setup_logging()
    run()
