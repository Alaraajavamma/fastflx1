# FastFLX1

FastFLX1 is a utility application for FuriOS/Linux Phones (FLX1). It provides various tweaks and tools to enhance the user experience.

## Features

*   **GUI Interface:** Modern GTK4/Libadwaita application to manage tweaks.
*   **Alarm Volume Fix:** Ensures alarm plays at full volume.
*   **Gesture Shortcuts:** Edge swipe gestures for window management.
*   **Andromeda Guard:** Fixes OSK issues when running Andromeda (Android).
*   **System Actions:** Switch between Staging/Production environments, install Branchy app store.
*   **Quick Actions:** Screenshot, Flashlight, Kill Apps.
*   **Shared Folders:** Manage file sharing between Linux and Android (Andromeda).

## Installation

### Debian Package (Recommended)

Build and install the package:

```bash
dpkg-buildpackage -us -uc
sudo apt install ../fastflx1_*.deb
```

### Manual

Ensure dependencies are installed:
```bash
sudo apt install python3-gi python3-loguru python3-requests python3-psutil libadwaita-1-0 gir1.2-adw-1 lisgd wtype curl inotify-tools bindfs
```

Install the python package:
```bash
pip install .
```

## Usage

Launch the application from the app drawer or run:

```bash
fastflx1
```

### CLI Options

*   `fastflx1 --action screenshot`
*   `fastflx1 --action flashlight`
*   `fastflx1 --monitor alarm` (Internal use)

## License

MIT
