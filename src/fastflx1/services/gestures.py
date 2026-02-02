import os
import subprocess
import signal
import sys
from fastflx1.utils import logger

class GestureMonitor:
    def __init__(self):
        self.device = os.environ.get("LISGD_INPUT_DEVICE", "/dev/input/event2")
        self.process = None

    def start(self):
        logger.info(f"Starting lisgd on {self.device}")

        # Arguments from the original script
        # -g "1,RL,B,*,R,setsid -f wtype -M alt -P tab -m alt -p tab"
        # -g "1,LR,B,*,R,setsid -f wtype -M alt -M shift -P tab -m alt -m shift -p tab"
        # -g "1,LR,L,L,R,setsid -f wtype -M alt -P F4 -m alt -p F4"
        # -g "1,LR,L,S,R,setsid -f wtype -k XF86Back"

        cmd = [
            "lisgd",
            "-d", self.device,
            "-g", "1,RL,B,*,R,setsid -f wtype -M alt -P tab -m alt -p tab",
            "-g", "1,LR,B,*,R,setsid -f wtype -M alt -M shift -P tab -m alt -m shift -p tab",
            "-g", "1,LR,L,L,R,setsid -f wtype -M alt -P F4 -m alt -p F4",
            "-g", "1,LR,L,S,R,setsid -f wtype -k XF86Back"
        ]

        logger.debug(f"Executing: {' '.join(cmd)}")

        try:
            # We replace the current process with lisgd, acting as a wrapper
            # This is efficient as we don't need to keep python running if it's just a launcher.
            # However, if we want to add features later, we might want to keep python running.
            # For now, let's use subprocess to keep control if needed, but 'exec' is cleaner for a simple wrapper.
            # But the requirement is "Convert scripst to python since then we can easily support deb packaging."
            # and "Start monitors in systemd services."
            # A python service running a subprocess is fine.

            self.process = subprocess.Popen(cmd)
            self.process.wait()
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logger.error(f"Error running lisgd: {e}")

    def stop(self):
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
    from fastflx1.utils import setup_logging
    setup_logging()
    run()
