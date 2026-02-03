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
from loguru import logger
from tweak_flx1s.utils import run_command
from tweak_flx1s.const import HOME_DIR

class AndromedaManager:
    """
    Manages shared folders between Linux and Andromeda (Android).
    Most methods here require ROOT privileges.
    """

    ANDROID_UID = 1023
    LINUX_EXCLUDE_FOLDERS = ["Android", "Android-Share"]
    ANDROID_EXCLUDE_FOLDERS = ["Host", "Linux-Share"]
    FSTAB_MARKER_BEGIN = "# BEGIN ANDROMEDA MOUNTS"
    FSTAB_MARKER_END = "# END ANDROMEDA MOUNTS"

    def __init__(self, user=None):
        if user:
            self.HOST_USER = user
        else:
            self.HOST_USER = os.environ.get("SUDO_USER") or os.environ.get("PKEXEC_USER") or os.environ.get("USER")
        self._reinit_paths()

    def _reinit_paths(self):
        """Re-initializes paths based on the host user."""
        self.HOST_HOME = os.path.expanduser(f"~{self.HOST_USER}") if self.HOST_USER else HOME_DIR
        self.ANDROID_STORAGE_SOURCE = os.path.join(self.HOST_HOME, ".local/share/andromeda/data/media/0")
        self.LINUX_MOUNT_BASE = os.path.join(self.ANDROID_STORAGE_SOURCE, "Linux-Share")
        self.ANDROID_MOUNT_BASE = os.path.join(self.HOST_HOME, "Android-Share")

    @staticmethod
    def _is_excluded(name, exclude_list):
        return name in exclude_list

    def is_mounted(self):
        """Checks if shared folders are currently mounted."""
        mounts = run_command("mount", check=False)
        return self.LINUX_MOUNT_BASE in mounts or self.ANDROID_MOUNT_BASE in mounts

    def toggle_mount(self):
        """Toggles the mount state."""
        if self.is_mounted():
            self.unmount()
            return False
        else:
            self.mount()
            return True

    def mount(self):
        """Mounts shared folders."""
        if os.geteuid() != 0:
            logger.error("Mount operation requires root privileges.")
            return False

        logger.info(f"Target User: {self.HOST_USER}")

        self.unmount()

        fstab_entries = []

        logger.info("Mounting Linux -> Android...")
        self._ensure_dir(self.LINUX_MOUNT_BASE, self.ANDROID_UID, self.ANDROID_UID, 0o775)

        for item in os.listdir(self.HOST_HOME):
            if item.startswith("."): continue
            if self._is_excluded(item, self.LINUX_EXCLUDE_FOLDERS): continue

            source = os.path.join(self.HOST_HOME, item)
            if not os.path.isdir(source): continue

            target = os.path.join(self.LINUX_MOUNT_BASE, item)
            self._ensure_dir(target, self.ANDROID_UID, self.ANDROID_UID, 0o775)

            try:
                run_command(["mount", "--bind", source, target])
                fstab_entries.append(f"{source} {target} none bind 0 0")
            except Exception as e:
                logger.error(f"Failed to mount {item}: {e}")

        logger.info("Mounting Android -> Linux...")
        run_command(["sudo", "-u", self.HOST_USER, "mkdir", "-p", self.ANDROID_MOUNT_BASE])
        run_command(["chmod", "775", self.ANDROID_MOUNT_BASE])

        if os.path.exists(self.ANDROID_STORAGE_SOURCE):
            for item in os.listdir(self.ANDROID_STORAGE_SOURCE):
                if item.startswith("."): continue
                if self._is_excluded(item, self.ANDROID_EXCLUDE_FOLDERS): continue

                source = os.path.join(self.ANDROID_STORAGE_SOURCE, item)
                if not os.path.isdir(source): continue

                target = os.path.join(self.ANDROID_MOUNT_BASE, item)

                run_command(["sudo", "-u", self.HOST_USER, "mkdir", "-p", target])
                run_command(["chmod", "775", target])

                try:
                    run_command(["mount", "--bind", source, target])
                    fstab_entries.append(f"{source} {target} none bind 0 0")
                except Exception as e:
                    logger.error(f"Failed to mount {item}: {e}")
        else:
            logger.warning(f"Andromeda storage not found: {self.ANDROID_STORAGE_SOURCE}")

        self._update_fstab(fstab_entries)

        service = f"tweak-flx1s-andromeda-fs@{self.HOST_USER}.service"
        logger.info(f"Starting service {service}...")
        try:
            run_command(["systemctl", "enable", "--now", service])
        except Exception as e:
            logger.error(f"Failed to start service {service}: {e}")

        return True

    def unmount(self):
        """Unmounts shared folders."""
        if os.geteuid() != 0:
            logger.error("Unmount operation requires root privileges.")
            return False

        service = f"tweak-flx1s-andromeda-fs@{self.HOST_USER}.service"
        logger.info(f"Stopping service {service}...")
        try:
            run_command(["systemctl", "disable", "--now", service])
        except Exception as e:
            logger.error(f"Failed to stop service {service}: {e}")

        logger.info("Unmounting shared folders...")

        mounts = run_command("mount").splitlines()
        targets = []
        for line in mounts:
            if self.LINUX_MOUNT_BASE in line or self.ANDROID_MOUNT_BASE in line:
                parts = line.split(" on ")
                if len(parts) > 1:
                    target = parts[1].split(" type ")[0]
                    targets.append(target)

        targets.sort(reverse=True)

        for target in targets:
            try:
                run_command(["umount", "-l", target])
            except Exception:
                pass

        if os.path.exists(self.ANDROID_MOUNT_BASE):
            try:
                os.rmdir(self.ANDROID_MOUNT_BASE)
            except OSError:
                pass

        if os.path.exists(self.LINUX_MOUNT_BASE):
            try:
                os.rmdir(self.LINUX_MOUNT_BASE)
            except OSError:
                pass

        self._clean_fstab()

    def watch(self):
        """
        The main loop for permission guard.
        Should be run by systemd or background process.
        """
        if os.geteuid() != 0:
            logger.error("Must be root.")
            return

        logger.info("Permission Guardian: Starting watch...")

        watch_dirs = []
        for item in os.listdir(self.HOST_HOME):
            if item.startswith("."): continue
            if self._is_excluded(item, self.LINUX_EXCLUDE_FOLDERS): continue
            path = os.path.join(self.HOST_HOME, item)
            if os.path.isdir(path):
                watch_dirs.append(path)

        if os.path.exists(self.ANDROID_MOUNT_BASE):
            watch_dirs.append(self.ANDROID_MOUNT_BASE)

        for d in watch_dirs:
            cmd = ["setfacl", "-R",
                   "-m", f"m:rwx,u:{self.HOST_USER}:rwx,d:u:{self.HOST_USER}:rwx,u:{self.ANDROID_UID}:rwx,d:u:{self.ANDROID_UID}:rwx",
                   d]
            run_command(cmd)

        logger.info("Initial sync done. Watching...")

        cmd = ["inotifywait", "-m", "-r", "-q", "-e", "create", "-e", "moved_to", "--format", "%w%f"] + watch_dirs

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
        try:
            while True:
                line = process.stdout.readline()
                if not line: break
                new_file = line.strip()
                logger.info(f"New file detected: {new_file}")

                cmd_update = ["setfacl", "-m", f"m:rwx,u:{self.HOST_USER}:rwx,u:{self.ANDROID_UID}:rwx", new_file]
                run_command(cmd_update, check=False)
        except KeyboardInterrupt:
            process.terminate()

    def _ensure_dir(self, path, uid, gid, mode):
        """Ensures a directory exists with specific permissions."""
        if not os.path.exists(path):
            os.makedirs(path)
        os.chown(path, int(uid), int(gid))
        os.chmod(path, mode)

    def _update_fstab(self, entries):
        """Updates fstab with new mount entries."""
        if not entries: return
        try:
            with open("/etc/fstab", "r") as f:
                lines = f.readlines()

            new_lines = []
            skip = False
            for line in lines:
                if self.FSTAB_MARKER_BEGIN in line:
                    skip = True
                if not skip:
                    new_lines.append(line)
                if self.FSTAB_MARKER_END in line:
                    skip = False

            while new_lines and new_lines[-1].strip() == "":
                new_lines.pop()

            new_lines.append("\n" + self.FSTAB_MARKER_BEGIN + "\n")
            new_lines.extend([e + "\n" for e in entries])
            new_lines.append(self.FSTAB_MARKER_END + "\n")

            with open("/etc/fstab", "w") as f:
                f.writelines(new_lines)

        except Exception as e:
            logger.error(f"Error updating fstab: {e}")

    def _clean_fstab(self):
        """Removes Andromeda entries from fstab."""
        try:
            with open("/etc/fstab", "r") as f:
                lines = f.readlines()

            new_lines = []
            skip = False
            found = False
            for line in lines:
                if self.FSTAB_MARKER_BEGIN in line:
                    skip = True
                if not skip:
                    new_lines.append(line)
                if self.FSTAB_MARKER_END in line:
                    skip = False

            if found:
                with open("/etc/fstab", "w") as f:
                    f.writelines(new_lines)
        except Exception as e:
            logger.error(f"Error cleaning fstab: {e}")
