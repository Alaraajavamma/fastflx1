import os

APP_ID = "com.gitlab.fastflx1"
APP_NAME = "FastFLX1"
VERSION = "0.1.0"

# Directories
HOME_DIR = os.path.expanduser("~")
CONFIG_DIR = os.path.join(HOME_DIR, ".config", "fastflx1")
CACHE_DIR = os.path.join(HOME_DIR, ".cache", "fastflx1")

# Service Names for Systemd
SERVICE_ALARM = "fastflx1-alarm.service"
SERVICE_GUARD = "fastflx1-guard.service"
SERVICE_GESTURES = "fastflx1-gestures.service"

# Andromeda
ANDROMEDA_ANDROID_MOUNT_BASE = os.path.join(HOME_DIR, "Android-Share")
ANDROMEDA_LINUX_MOUNT_BASE_REL = ".local/share/andromeda/data/media/0/Linux-Share"

# Icons
ICON_APP = "fastflx1" # Assuming we install the icon
