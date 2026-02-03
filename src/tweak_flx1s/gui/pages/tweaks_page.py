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
import shutil
import shlex
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
from tweak_flx1s.const import SERVICE_ALARM, SERVICE_GUARD, SERVICE_GESTURES, APP_NAME
from tweak_flx1s.utils import run_command, logger
from tweak_flx1s.system.andromeda import AndromedaManager
from tweak_flx1s.system.sounds import SoundManager
from tweak_flx1s.gui.dialogs import ExecutionDialog
from tweak_flx1s.gui.pages.info_page import InfoPage

try:
    _
except NameError:
    from gettext import gettext as _

class TweaksPage(Adw.PreferencesPage):
    """
    Page for general tweaks.
    Includes: Alarm Volume, Andromeda Guard (OSK),
    Android Shared Folders, Custom Sounds, Appearance.
    """
    def __init__(self, window, **kwargs):
        super().__init__(title=_("Tweaks"), icon_name="preferences-system-symbolic", **kwargs)
        self.window = window
        self.andromeda = AndromedaManager()
        self.sounds = SoundManager()

        appearance_grp = Adw.PreferencesGroup(title=_("Appearance"))
        self.add(appearance_grp)

        css_row = Adw.SwitchRow(title=_("GTK3 CSS Tweak"), subtitle=_("Apply custom UI scaling tweaks for GTK3 apps"))
        css_row.set_active(self._is_gtk_tweak_active())
        css_row.connect("notify::active", self._on_css_toggled)
        appearance_grp.add(css_row)

        svc_group = Adw.PreferencesGroup(title=_("Background Services"))
        self.add(svc_group)

        self._add_service_row(svc_group, _("Alarm Volume Fix"), _("Ensure alarm plays at full volume"), SERVICE_ALARM)
        self._add_service_row(svc_group, _("Andromeda Guard"), _("Prevent OSK issues"), SERVICE_GUARD)

        shared_group = Adw.PreferencesGroup(title=_("Andromeda Integration"))
        self.add(shared_group)

        shared_row = Adw.SwitchRow(title=_("Shared Folders"), subtitle=_("Mount ~/.local/share/andromeda to ~/Android-Share"))
        shared_row.set_active(self.andromeda.is_mounted())
        shared_row.connect("notify::active", self._on_shared_toggled)
        shared_group.add(shared_row)

        sound_group = Adw.PreferencesGroup(title=_("Audio"))
        self.add(sound_group)

        sound_row = Adw.SwitchRow(title=_("Custom Sound Theme"), subtitle=_("Use fastflx1 custom sounds"))
        sound_row.set_active(self.sounds.is_custom_theme_active())
        sound_row.connect("notify::active", self._on_sound_toggled)
        sound_group.add(sound_row)

    def _get_css_paths(self):
        """Returns (source_path, target_path) for GTK3 CSS."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        source = os.path.join(base_dir, "data", "gtk.css")
        target = os.path.expanduser("~/.config/gtk-3.0/gtk.css")
        return source, target

    def _is_gtk_tweak_active(self):
        """Checks if the custom GTK CSS is applied."""
        source, target = self._get_css_paths()
        if not os.path.exists(target):
            return False
        return True

    def _on_css_toggled(self, row, param):
        source, target = self._get_css_paths()
        active = row.get_active()

        if active:
            try:
                target_dir = os.path.dirname(target)
                os.makedirs(target_dir, exist_ok=True)
                shutil.copy2(source, target)
                logger.info(f"Applied GTK3 CSS tweak to {target}")
            except Exception as e:
                logger.error(f"Failed to apply GTK3 CSS tweak: {e}")
        else:
            try:
                if os.path.exists(target):
                    os.remove(target)
                    logger.info(f"Removed GTK3 CSS tweak from {target}")
            except Exception as e:
                logger.error(f"Failed to remove GTK3 CSS tweak: {e}")

    def _add_service_row(self, group, title, subtitle, service_name):
        row = Adw.SwitchRow(title=title, subtitle=subtitle)
        row.set_active(self._is_active(service_name))
        row.connect("notify::active", self._on_switch_toggled, service_name)
        group.add(row)

    def _is_active(self, service):
        try:
            out = run_command(f"systemctl --user is-enabled {service}", check=False)
            return out == "enabled"
        except Exception as e:
            logger.warning(f"Failed to check status for {service}: {e}")
            return False

    def _on_switch_toggled(self, row, param, service):
        action = "enable --now" if row.get_active() else "disable --now"
        logger.info(f"{action} {service}")
        run_command(f"systemctl --user {action} {service}", check=False)

    def _on_shared_toggled(self, row, param):
        is_active = row.get_active()
        user = GLib.get_user_name()
        if is_active:
            if not self.andromeda.is_mounted():
                cmd = f"python3 -c \"import sys; from tweak_flx1s.system.andromeda import AndromedaManager; AndromedaManager(user=sys.argv[1]).mount()\" {shlex.quote(user)}"
                dlg = ExecutionDialog(self.window, _("Mounting Shared Folders"), cmd, as_root=True)
                dlg.present()
        else:
            if self.andromeda.is_mounted():
                cmd = f"python3 -c \"import sys; from tweak_flx1s.system.andromeda import AndromedaManager; AndromedaManager(user=sys.argv[1]).unmount()\" {shlex.quote(user)}"
                dlg = ExecutionDialog(self.window, _("Unmounting Shared Folders"), cmd, as_root=True)
                dlg.present()

    def _on_sound_toggled(self, row, param):
        if row.get_active():
            self.sounds.enable_custom_theme()
        else:
            self.sounds.disable_custom_theme()
