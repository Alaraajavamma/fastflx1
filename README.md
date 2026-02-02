# Tweak-FLX1s

Tweak-FLX1s is a comprehensive utility and tweaking tool designed for FuriOS and Linux Phones (specifically FuriPhoneFLX1 and FLX1s). It provides a modern GTK4/Libadwaita interface to manage system settings, services, and enhancements.

## Features

### 1. Background Services
*   **Alarm Volume Fix:** Ensures that the alarm clock plays at full volume and wakes up the device even if it is muted or screen is off.
*   **Andromeda Guard:** Prevents the On-Screen Keyboard (OSK) from interfering with Andromeda (Android compatibility layer) applications by managing the keyboard state during session transitions.
*   **Gesture Shortcuts:** Enables edge swipe gestures (using `lisgd`) to trigger configurable actions like app switching, closing windows, or custom commands.

### 2. Button Actions
Configure actions for physical button presses (Short, Double, Long Press).
*   **Locked State:** Define specific commands when the screen is locked (e.g., Toggle Flashlight).
*   **Unlocked State:** Launch commands or open a custom "Wofi" menu with up to 7 items.
*   **Predefined Actions:** Quickly assign actions like Copy, Paste, Screenshot, Flashlight, or Kill Window.

### 3. Phofono Management
Easily install and manage **Phofono**, a replacement stack for Calls and Chatty.
*   Automated installation from Git.
*   Handles system diversions to disable stock apps safely.
*   Manages background services (`ofono-toned`, `calls-daemon`).

### 4. Andromeda Shared Folders
Manage file sharing between the Linux host and the Android container.
*   **Mount/Unmount:** Bind mount Linux home folders to Android and vice versa.
*   **Permission Guardian:** Automatically watches and fixes permission issues (ACLs) for shared files to ensure both systems can read/write.

### 5. System Tweaks
*   **Environment Switching:** Switch between Staging and Production repositories for FuriOS.
*   **System Upgrade:** Run a full system upgrade with a single click.
*   **Branchy:** Install the experimental "Branchy" app store.
*   **Keyboard Management:** Switch between Squeekboard and Phosh-OSK (Stub).
*   **Weather:** Add locations to GNOME Weather from the app.

### 6. Security
*   **Password Policy:** Set the minimum password length (modifies PAM configuration).
*   **Fingerprint Authentication:** Enable fingerprint support on FuriPhoneFLX1 (configures `libpam-biomd` and `libpam-parallel`).

## Installation

Tweak-FLX1s is packaged as a Debian package.

```bash
sudo apt install tweak-flx1s
```

## Usage

Launch the application from the app drawer ("Tweak-FLX1s").

### CLI Arguments
The application also supports command-line arguments for triggers and services:

*   `--monitor [alarm|guard|gestures|andromeda-fs]`: Start a background monitor service.
*   `--action [screenshot|flashlight|kill-window|paste]`: Perform a one-off action.
*   `--trigger-gesture [index]`: Trigger a specific gesture action.
*   `--[short|double|long]-press`: Handle button press events.

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
