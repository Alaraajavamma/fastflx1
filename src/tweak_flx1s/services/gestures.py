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
import subprocess
import shutil
from loguru import logger
from tweak_flx1s.utils import get_device_model
from tweak_flx1s.actions.gestures import GesturesManager

class GestureMonitor:
    """Monitors gestures using lisgd."""
    def __init__(self):
        self.device = os.environ.get("LISGD_INPUT_DEVICE")
        if not self.device:
            model = get_device_model()
            if model == "FuriPhoneFLX1s":
                self.device = "/dev/input/event3"
            else:
                self.device = "/dev/input/event2"

        self.process = None
        self.manager = GesturesManager()

    def start(self):
        """Starts the lisgd process with configured gestures."""
        if not self.manager.config.get("enabled", False):
            logger.info("Gestures are disabled in config.")
            return

        logger.info(f"Starting lisgd on {self.device}")

        cmd = ["lisgd", "-d", self.device]

        gestures = self.manager.config.get("gestures", [])
        executable = shutil.which("tweak-flx1s") or "tweak-flx1s"

        for idx, gesture in enumerate(gestures):
            spec = gesture.get("spec")
            if not spec:
                logger.warning(f"Skipping gesture {idx} without spec")
                continue

            action_cmd = f"{executable} --trigger-gesture {idx}"
            full_arg = f"{spec},{action_cmd}"
            cmd.extend(["-g", full_arg])

        logger.debug(f"Executing: {' '.join(cmd)}")

        try:
            self.process = subprocess.Popen(cmd)
            self.process.wait()
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logger.error(f"Error running lisgd: {e}")

    def stop(self):
        """Stops the lisgd process."""
        if self.process:
            logger.info("Stopping lisgd...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

def run():
    monitor = GestureMonitor()
    monitor.start()

if __name__ == "__main__":
    from tweak_flx1s.utils import setup_logging
    setup_logging()
    run()
