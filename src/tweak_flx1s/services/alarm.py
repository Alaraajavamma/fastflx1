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
import os
import subprocess
from gi.repository import GLib, Gio
from tweak_flx1s.utils import logger, run_command

class AlarmMonitor:
    """Monitors alarm events to ensure wake-up."""
    def __init__(self):
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.loop = GLib.MainLoop()

    def start(self):
        """Starts the monitoring process."""
        logger.info("Starting Alarm Monitor")
        self._monitor_process()

    def _monitor_process(self):
        """
        Runs dbus-monitor to intercept TriggerFeedback method calls.
        This is required because we need to see method calls destined for other services.
        """
        cmd = ["dbus-monitor", "type='method_call',interface='org.sigxcpu.Feedback',member='TriggerFeedback'"]
        logger.debug(f"Running: {' '.join(cmd)}")

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        logger.info("Listening for alarm events...")
        try:
            while True:
                line = process.stdout.readline()
                if not line:
                    break

                if "org.gnome.clocks" in line:
                    found_event = False
                    for _ in range(5):
                        next_line = process.stdout.readline()
                        if "alarm-clock-elapsed" in next_line:
                            found_event = True
                            break

                    if found_event:
                        self._perform_action()

        except Exception as e:
            logger.error(f"Error in alarm monitor: {e}")
        finally:
            process.terminate()

    def _perform_action(self):
        """Wakes up the screen and maximizes volume."""
        logger.info("Alarm clock event detected!")

        try:
            with open("/sys/class/leds/lcd-backlight/brightness", "r") as f:
                brightness = int(f.read().strip())

            if brightness == 0:
                logger.info("Screen is off, waking up/pressing power...")
                run_command("wtype -P XF86PowerOff", check=False)
        except FileNotFoundError:
            logger.warning("Could not read brightness file.")
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
