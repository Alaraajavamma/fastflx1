import sys
import os
from gi.repository import GLib, Gio
from tweak_flx1s.utils import logger, run_command

class AlarmMonitor:
    def __init__(self):
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.loop = GLib.MainLoop()

    def start(self):
        logger.info("Starting Alarm Monitor")
        # Subscribe to TriggerFeedback method calls on org.sigxcpu.Feedback
        # Since we can't easily eavesdrop on method calls without being the destination or monitoring all,
        # we might need to use the 'dbus-monitor' approach if we can't register a filter.
        # However, monitoring signals is standard. The original script used `dbus-monitor` which sees everything.
        # Python DBus libs usually listen to Signals. 'TriggerFeedback' looks like a method call.
        # If it is a method call, ordinary clients can't intercept it easily unless they are monitoring the bus.

        # The original script uses `dbus-monitor "type='method_call'..."`.
        # Replicating `dbus-monitor` in Python purely with Gio might be hard if we aren't a debugger.
        # But we can just use `subprocess` to run `dbus-monitor` and parse output, just like the bash script,
        # but handled cleanly in a thread or asyncio.
        # OR we can try to see if there is a signal we can use.
        # Given the requirements "Convert all scripts to python", wrapping `dbus-monitor` is a valid conversion
        # if direct API isn't available. But let's check if we can use a library.
        # Actually, `dbus-monitor` is a robust way to sniff.

        # Let's try to implement the parsing loop in Python.
        self._monitor_process()

    def _monitor_process(self):
        cmd = ["dbus-monitor", "type='method_call',interface='org.sigxcpu.Feedback',member='TriggerFeedback'"]
        logger.debug(f"Running: {' '.join(cmd)}")

        import subprocess
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        logger.info("Listening for alarm events...")
        try:
            while True:
                line = process.stdout.readline()
                if not line:
                    break

                # logic from original script:
                # if echo "$line" | grep -q '"org.gnome.clocks"'; then
                #   read -r next_line
                #   if echo "$next_line" | grep -q '"alarm-clock-elapsed"'; then

                if "org.gnome.clocks" in line:
                    # We need to peek or read next lines to confirm 'alarm-clock-elapsed'
                    # dbus-monitor output is multi-line for method arguments.
                    # We can read a few lines ahead.
                    found_event = False
                    for _ in range(5): # Read next few lines
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
        logger.info("Alarm clock event detected!")

        # Check brightness
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

        # Unmute and max volume
        run_command("amixer set Master 100% unmute", check=False)

def run():
    monitor = AlarmMonitor()
    monitor.start()

if __name__ == "__main__":
    from tweak_flx1s.utils import setup_logging
    setup_logging()
    run()
