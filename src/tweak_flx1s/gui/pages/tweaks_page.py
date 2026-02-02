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

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
from tweak_flx1s.const import SERVICE_ALARM, SERVICE_GUARD, SERVICE_GESTURES, APP_NAME
from tweak_flx1s.utils import run_command, logger
from tweak_flx1s.system.andromeda import AndromedaManager
from tweak_flx1s.system.sounds import SoundManager
from tweak_flx1s.gui.phofono_page import PhofonoPage
from tweak_flx1s.gui.pages.info_page import InfoPage

try:
    _
except NameError:
    from gettext import gettext as _

class TweaksPage(Adw.PreferencesPage):
    """
    Page for general tweaks.
    Includes: Phofono Settings, Alarm Volume, Andromeda Guard (OSK),
    Android Shared Folders, Custom Sounds.
    """
    def __init__(self, window, **kwargs):
        super().__init__(title="Tweaks", icon_name="preferences-system-symbolic", **kwargs)
        self.window = window
        self.andromeda = AndromedaManager()
        self.sounds = SoundManager()

        # Phofono Section
        phofono_grp = Adw.PreferencesGroup(title="Phofono")
        self.add(phofono_grp)

        phofono_btn = Gtk.Button(label="Phofono Settings")
        phofono_btn.set_valign(Gtk.Align.CENTER)
        phofono_btn.connect("clicked", self._open_phofono_settings)
        phofono_row = Adw.ActionRow(title="Configure Phofono")
        phofono_row.add_suffix(phofono_btn)
        phofono_grp.add(phofono_row)

        # Background Services
        svc_group = Adw.PreferencesGroup(title="Background Services")
        self.add(svc_group)

        self._add_service_row(svc_group, "Alarm Volume Fix", "Ensure alarm plays at full volume", SERVICE_ALARM)
        # Note: Andromeda Guard Service is now our python implementation
        self._add_service_row(svc_group, "Andromeda Guard", "Prevent OSK issues", SERVICE_GUARD)

        # Android Shared Folders
        shared_group = Adw.PreferencesGroup(title="Andromeda Integration")
        self.add(shared_group)

        shared_row = Adw.SwitchRow(title="Shared Folders", subtitle="Mount ~/.local/share/andromeda to ~/Android-Share")
        shared_row.set_active(self.andromeda.is_mounted())
        shared_row.connect("notify::active", self._on_shared_toggled)
        shared_group.add(shared_row)

        # Custom Sounds
        sound_group = Adw.PreferencesGroup(title="Audio")
        self.add(sound_group)

        sound_row = Adw.SwitchRow(title="Custom Sound Theme", subtitle="Use fastflx1 custom sounds")
        sound_row.set_active(self.sounds.is_custom_theme_active())
        sound_row.connect("notify::active", self._on_sound_toggled)
        sound_group.add(sound_row)

    def _open_phofono_settings(self, btn):
        # We can open the PhofonoPage as a dialog or just a transient window
        # Since it was a page in the stack, let's reuse it or instantiate it.
        # But PhofonoPage is complex.
        # Ideally, we should just show it.
        # Let's create a dialog window for it.

        win = Adw.Window(title="Phofono Settings", transient_for=self.window, modal=True)
        win.set_default_size(360, 600)

        # We need a toolbar view
        content = Adw.ToolbarView()
        win.set_content(content)

        header = Adw.HeaderBar()
        content.add_top_bar(header)

        # Reuse PhofonoPage logic, but maybe wrap it?
        # PhofonoPage inherits from Adw.PreferencesPage.
        page = PhofonoPage(self.window)
        content.set_content(page)

        win.present()

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
        if is_active:
            if not self.andromeda.mount():
                # Revert if failed (though strictly we can't easily revert the switch programmatically inside the handler without recursion loops if we aren't careful, but Adw usually handles it)
                # We should show error.
                pass
        else:
            self.andromeda.unmount()

    def _on_sound_toggled(self, row, param):
        if row.get_active():
            self.sounds.enable_custom_theme()
        else:
            self.sounds.disable_custom_theme()
