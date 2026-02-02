import os
import shutil
from tweak_flx1s.utils import logger, run_command
from tweak_flx1s.const import CACHE_DIR

class PhofonoManager:
    def check_installed(self):
        try:
             run_command("dpkg -s phofono", check=True)
             return True
        except:
             return False

    def prepare_install(self):
        logger.info("Preparing install: stopping services...")
        run_command("systemctl --user stop calls-daemon", check=False)
        run_command("systemctl --user mask calls-daemon", check=False)

        work_dir = os.path.join(CACHE_DIR, "phofono_install")
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)
        os.makedirs(work_dir, exist_ok=True)

        logger.info("Cloning phofono repo...")
        cmd = f"git clone https://gitlab.com/Alaraajavamma/phofono {work_dir}/phofono"
        run_command(cmd)

        return os.path.join(work_dir, "phofono")

    def get_install_root_cmd(self, repo_dir):
        script = f"""
set -e
cd "{repo_dir}"
echo "Installing package..."
apt install -y ./phofono_*.deb

echo "Configuring diversions..."
dpkg-divert --add --rename --divert /etc/xdg/autostart/sm.puri.Chatty-daemon.desktop.disabled /etc/xdg/autostart/sm.puri.Chatty-daemon.desktop || true
dpkg-divert --add --rename --divert /etc/xdg/autostart/org.gnome.Calls-daemon.desktop.disabled /etc/xdg/autostart/org.gnome.Calls-daemon.desktop || true
dpkg-divert --add --rename --divert /usr/share/applications/sm.puri.Chatty.desktop.disabled /usr/share/applications/sm.puri.Chatty.desktop || true
dpkg-divert --add --rename --divert /usr/share/applications/org.gnome.Calls.desktop.disabled /usr/share/applications/org.gnome.Calls.desktop || true

echo "Root tasks complete."
"""
        return script

    def finish_install(self):
        logger.info("Finishing install: configuring user services...")
        dbus_dir = os.path.expanduser("~/.local/share/dbus-1/services/")
        os.makedirs(dbus_dir, exist_ok=True)
        service_file = os.path.join(dbus_dir, "org.gnome.Calls.service")
        with open(service_file, "w") as f:
            f.write("[D-BUS Service]\nName=org.gnome.Calls\nExec=/bin/true")

        run_command("systemctl --user disable ofono-toned", check=False)
        run_command("systemctl --user mask ofono-toned", check=False)
        run_command("pkill -f ofono-toned", check=False)

        work_dir = os.path.join(CACHE_DIR, "phofono_install")
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)

    def get_uninstall_root_cmd(self):
        script = """
set -e
echo "Removing package..."
apt remove -y phofono

echo "Removing diversions..."
dpkg-divert --remove --rename /etc/xdg/autostart/sm.puri.Chatty-daemon.desktop || true
dpkg-divert --remove --rename /etc/xdg/autostart/org.gnome.Calls-daemon.desktop || true
dpkg-divert --remove --rename /usr/share/applications/sm.puri.Chatty.desktop || true
dpkg-divert --remove --rename /usr/share/applications/org.gnome.Calls.desktop || true

echo "Root tasks complete."
"""
        return script

    def finish_uninstall(self):
        logger.info("Finishing uninstall: restoring user services...")
        run_command("systemctl --user unmask calls-daemon", check=False)

        dbus_file = os.path.expanduser("~/.local/share/dbus-1/services/org.gnome.Calls.service")
        if os.path.exists(dbus_file):
            os.remove(dbus_file)

        run_command("systemctl --user daemon-reload", check=False)

        run_command("systemctl --user unmask ofono-toned", check=False)
        run_command("systemctl --user enable ofono-toned", check=False)
        run_command("systemctl --user start ofono-toned", check=False)
