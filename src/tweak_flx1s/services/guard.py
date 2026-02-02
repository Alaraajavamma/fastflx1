import sys
import time
import subprocess
from gi.repository import GLib, Gio
from tweak_flx1s.utils import logger, run_command

class AndromedaGuard:
    def __init__(self):
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.loop = GLib.MainLoop()
        self.settings = Gio.Settings.new("org.gnome.desktop.a11y.applications")
        self.app_name = "Andromeda display guard"

    def notify_with_countdown(self, seconds):
        for i in range(seconds, 0, -1):
            if i % 5 == 0 or i == seconds:
                timeout_ms = i * 1000
                run_command(
                    f"notify-send --icon='input-keyboard' --hint=int:transient:1 "
                    f"--expire-time={timeout_ms} --app-name='{self.app_name}' "
                    f"'OSK locked for {i} seconds'",
                    check=False
                )
            time.sleep(1)

    def enable_keyboard(self):
        self.settings.set_boolean("screen-keyboard-enabled", True)
        run_command(
            f"notify-send --icon='input-keyboard' --expire-time=3000 "
            f"--hint=int:transient:1 --app-name='{self.app_name}' "
            "'Andromeda is ready - OSK Unlocked'",
            check=False
        )
        logger.info("OSK Enabled")

    def disable_keyboard(self):
        self.settings.set_boolean("screen-keyboard-enabled", False)
        logger.info("OSK Disabled")

    def handle_session_reset(self):
        logger.info("Handling session reset")
        self.disable_keyboard()
        self.notify_with_countdown(20)
        self.enable_keyboard()

    def initial_setup(self):
        logger.info("Running initial setup")
        self.disable_keyboard()
        self.notify_with_countdown(40)
        self.enable_keyboard()

    def on_name_acquired(self, connection, sender_name, object_path, interface_name, signal_name, parameters, user_data):
        # parameters is a GVariant tuple. The first item is the name acquired.
        name = parameters.unpack()[0]
        if name == "io.furios.Andromeda.Session":
            logger.info(f"Detected NameAcquired: {name}")
            self.handle_session_reset()

    def start(self):
        # Initial setup
        self.initial_setup()

        # Monitor DBus for NameAcquired
        # The signal comes from org.freedesktop.DBus service, path /org/freedesktop/DBus, interface org.freedesktop.DBus
        self.bus.signal_subscribe(
            "org.freedesktop.DBus", # sender
            "org.freedesktop.DBus", # interface
            "NameAcquired",         # member
            "/org/freedesktop/DBus",# object path
            None,                   # arg0
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
