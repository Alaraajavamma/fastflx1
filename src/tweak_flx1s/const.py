import os

APP_ID = "io.FuriOS.Tweak-FLX1s"
APP_NAME = "Tweak-FLX1s"
VERSION = "0.1.0"

# Directories
HOME_DIR = os.path.expanduser("~")
CONFIG_DIR = os.path.join(HOME_DIR, ".config", "tweak-flx1s")
CACHE_DIR = os.path.join(HOME_DIR, ".cache", "tweak-flx1s")

# Service Names for Systemd
SERVICE_ALARM = "tweak-flx1s-alarm.service"
SERVICE_GUARD = "tweak-flx1s-guard.service"
SERVICE_GESTURES = "tweak-flx1s-gestures.service"

# Andromeda
ANDROMEDA_ANDROID_MOUNT_BASE = os.path.join(HOME_DIR, "Android-Share")
ANDROMEDA_LINUX_MOUNT_BASE_REL = ".local/share/andromeda/data/media/0/Linux-Share"

# Icons
ICON_APP = "io.FuriOS.Tweak-FLX1s"
