# Tweak-FLX1s

Tweak-FLX1s is a comprehensive utility and tweaking tool designed for FuriOS and Linux Phones (specifically FuriPhoneFLX1 and FLX1s). It provides a modern GTK4/Libadwaita interface to manage system settings, services, and enhancements.

## Features

The application is organized into three main tabs:

### 1. System
Manage core system components, packages, and security settings.

*   **Keyboard Management:**
    *   Switch between **Squeekboard** and **Phosh-OSK**.
    *   Install a custom **Finnish Layout** for Squeekboard.
*   **Configuration:**
    *   **Enforce App Wofi Config:** Apply Tweak-FLX1s styling and configuration to the Wofi launcher.
*   **Environment:**
    *   Toggle between **Staging** and **Production** repositories for FuriOS.
*   **Updates:**
    *   **System Upgrade:** Run a full system upgrade (`apt upgrade`) with a single click.
*   **Applications:**
    *   **Squeekboard:** Install or remove the on-screen keyboard.
    *   **FLX1s-Bat-Mon:** Install a custom battery monitor utility.
    *   **Phofono:** Install/Remove the alternative Phofono stack (replacing Calls/Chatty).
    *   **Branchy:** Install/Remove the experimental "Branchy" app store.
    *   **DebUI:** Install/Remove the Debian Package Installer UI.
*   **Security:**
    *   **Short Passwords:** Enable support for 1-character passwords (modifies PAM).
    *   **Change Password:** GUI to change the current user's password.
    *   **Fingerprint Authentication:** Configure PAM to support the FuriPhoneFLX1 fingerprint sensor.

### 2. Tweaks
Customize the look, feel, and background behavior of your device.

*   **Appearance:**
    *   **GTK3 CSS Tweak:** Apply custom UI scaling tweaks for legacy GTK3 applications.
*   **Background Services:**
    *   **Alarm Volume Fix:** Ensures that the alarm clock plays at full volume and wakes up the device even if it is muted.
    *   **Andromeda Guard:** Prevents the On-Screen Keyboard (OSK) from interfering with Andromeda (Android compatibility layer) applications.
*   **Andromeda Integration:**
    *   **Shared Folders:** Bind mount your Linux home folders to the Android container (`~/Android-Share`), with automatic permission fixing.
*   **Audio:**
    *   **Custom Sound Theme:** Enable the "fastflx1" custom sound theme.

### 3. Actions
Configure hardware buttons and touch gestures for quick access to functions.

*   **Hardware Buttons:**
    *   Configure actions for **Short**, **Double**, and **Long** presses of the assistant button.
    *   Define different actions for **Locked** and **Unlocked** states.
    *   Trigger actions like Flashlight, Screenshot, Kill Window, or open a custom **Wofi Menu**.
*   **Touch Gestures:**
    *   Create and manage edge swipe gestures (using `lisgd`).
    *   Configure direction (Up, Down, Left, Right, Diagonals), edge, and number of fingers.
    *   Assign commands to gestures.

## CLI Arguments

The application supports command-line arguments for triggers and background services:

*   `--monitor [alarm|guard|gestures|andromeda-fs]`: Start a background monitor service.
*   `--action [screenshot|flashlight|kill-window|paste]`: Perform a one-off action.
*   `--trigger-gesture [index]`: Trigger a specific gesture action.
*   `--[short|double|long]-press`: Handle button press events.

## Build Dependencies

Before building, ensure you have the necessary dependencies installed:

```bash
sudo apt update
sudo apt install build-essential debhelper dh-python python3-setuptools \
                 python3-gi python3-loguru python3-requests python3-psutil \
                 libadwaita-1-dev
```

## Build

To build the package from source:

```bash
dpkg-buildpackage -us -uc
```

## Installation

Install the generated package. This will automatically pull in all runtime dependencies:

```bash
sudo apt install ./tweak-flx1s*.deb
```

## Uninstallation

To remove the package and restore system configurations:

```bash
sudo apt remove tweak-flx1s
```

This will:
*   Remove the application and services.
*   Restore modified PAM configurations (sudo, polkit, etc.) from backups.
*   Clean up user configuration files.
*   Restore permissions on shared folders.

## Copyright

Copyright (C) 2024 Alaraajavamma <aki@urheiluaki.fi>
License: GPL-3.0-or-later
