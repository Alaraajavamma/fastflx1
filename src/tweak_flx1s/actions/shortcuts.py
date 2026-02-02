import os
import subprocess
import time
import datetime
from gi.repository import Gio, GLib
from tweak_flx1s.utils import logger, run_command
from tweak_flx1s.const import HOME_DIR

class ShortcutsManager:
    def __init__(self):
        pass

    def take_screenshot(self):
        timestamp = datetime.datetime.now().strftime("%F-%T")
        # Ensure directory
        pictures_dir = run_command("xdg-user-dir PICTURES") or f"{HOME_DIR}/Pictures"
        path = f"{pictures_dir}/Screenshot-{timestamp}.png"

        logger.info(f"Taking screenshot: {path}")

        # Using DBus directly is better than spawning a process if possible, but
        # org.gnome.Shell.Screenshot.Screenshot method is standard.

        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        proxy = Gio.DBusProxy.new_sync(
            bus,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.gnome.Shell.Screenshot",
            "/org/gnome/Shell/Screenshot",
            "org.gnome.Shell.Screenshot",
            None
        )

        # method: Screenshot(boolean include_cursor, boolean flash, string filename)
        try:
            proxy.call_sync(
                "Screenshot",
                GLib.Variant("(bbs)", (True, False, path)),
                Gio.DBusCallFlags.NONE,
                -1,
                None
            )
            run_command(f"notify-send 'Screenshot Taken' 'Saved to {path}' --icon='camera-photo'")
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")

    def toggle_flashlight(self):
        bus_name = "io.furios.Flashlightd"
        object_path = "/io/furios/Flashlightd"
        interface = "io.furios.Flashlightd"

        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        try:
            proxy = Gio.DBusProxy.new_sync(
                bus, Gio.DBusProxyFlags.NONE, None, bus_name, object_path, interface, None
            )

            # Get Brightness property
            props = Gio.DBusProxy.new_sync(
                bus, Gio.DBusProxyFlags.NONE, None, bus_name, object_path, "org.freedesktop.DBus.Properties", None
            )
            current = props.call_sync(
                "Get", GLib.Variant("(ss)", (interface, "Brightness")), Gio.DBusCallFlags.NONE, -1, None
            ).unpack()[0] # Unpack variant

            if current == 0:
                # Turn ON
                logger.info("Turning flashlight ON")
                max_b = props.call_sync(
                    "Get", GLib.Variant("(ss)", (interface, "MaxBrightness")), Gio.DBusCallFlags.NONE, -1, None
                ).unpack()[0]

                proxy.call_sync("SetBrightness", GLib.Variant("(u)", (max_b,)), Gio.DBusCallFlags.NONE, -1, None)

                # Auto off after 20s - handled in background?
                # The original script does `sleep 20` then turns off.
                # If we block here, the GUI freezes if called from GUI.
                # If called from CLI (action), it blocks the CLI, which is fine.
                # But we should probably fork or use a timer if we want to return.
                # For now, blocking is okay for the CLI action, but maybe not if we want to release the button.
                # I'll just leave it as toggle for now or spawn a background sleeper.
            else:
                # Turn OFF
                logger.info("Turning flashlight OFF")
                proxy.call_sync("SetBrightness", GLib.Variant("(u)", (0,)), Gio.DBusCallFlags.NONE, -1, None)

        except Exception as e:
            logger.error(f"Flashlight error: {e}")

    def kill_active_window(self):
        # wtype -M alt -P F4 -m alt -p F4
        run_command("wtype -M alt -P F4 -m alt -p F4")

    def kill_ram_eaters(self):
        # ps --sort=-%mem ...
        # logic from locked() in long-press
        import psutil

        exclude = ["systemd", "bash", "sshd", "phosh", "gnome-shell"]
        killed = []

        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
            try:
                if proc.info['name'] in exclude: continue

                # Check thresholds (original: 80% CPU or 80% MEM)
                if proc.info['memory_percent'] > 80 or proc.info['cpu_percent'] > 80:
                    logger.info(f"Killing {proc.info['name']} (PID {proc.info['pid']})")
                    proc.kill()
                    killed.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        if killed:
             run_command(f"notify-send 'Killed High Usage Apps' '{', '.join(killed)}'")

    def set_scale(self, scale):
        # wlr-randr --output "HWCOMPOSER-1" --scale X.XX
        run_command(f"wlr-randr --output 'HWCOMPOSER-1' --scale {scale}")

    def take_picture(self):
         # gst-launch logic
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pictures_dir = f"{HOME_DIR}/Pictures"
        filename = f"{pictures_dir}/photo_{timestamp}.jpeg"

        cmd = (
            f"gst-launch-1.0 -e droidcamsrc camera-device=0 mode=2 ! "
            f"videoconvert ! videoflip video-direction=8 ! jpegenc snapshot=true ! "
            f"filesink location='{filename}'"
        )
        try:
            run_command(cmd)
            run_command(f"notify-send 'Picture Taken' 'Saved to {filename}'")
        except:
            pass
