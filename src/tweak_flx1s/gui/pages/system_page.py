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
from tweak_flx1s.utils import run_command, logger
from tweak_flx1s.gui.dialogs import ExecutionDialog
from tweak_flx1s.system.package_manager import PackageManager
from tweak_flx1s.system.keyboard import KeyboardManager
from tweak_flx1s.system.pam import PamManager
from tweak_flx1s.utils import get_device_model

try:
    _
except NameError:
    from gettext import gettext as _

class SystemPage(Adw.PreferencesPage):
    """
    Page for system-level settings.
    Includes: Keyboard, Environment, Updates, Security, Bat-Mon.
    """
    def __init__(self, window, **kwargs):
        super().__init__(title="System", icon_name="emblem-system-symbolic", **kwargs)
        self.window = window
        self.pkg_mgr = PackageManager()
        self.kbd_mgr = KeyboardManager()

        def run_pkg_cmd(title, cmd):
            try:
                dlg = ExecutionDialog(self.window, title, cmd, as_root=True)
                dlg.present()
            except Exception as e:
                logger.error(f"Failed to start execution dialog for {title}: {e}")

        # Keyboard Section
        kbd_group = Adw.PreferencesGroup(title="Keyboard")
        self.add(kbd_group)

        if not self.kbd_mgr.check_squeekboard_installed():
            install_row = Adw.ActionRow(title="Squeekboard Missing")
            install_btn = Gtk.Button(label="Install")
            install_btn.set_valign(Gtk.Align.CENTER)
            install_btn.connect("clicked", lambda x: run_pkg_cmd("Installing Squeekboard", self.kbd_mgr.install_squeekboard()))
            install_row.add_suffix(install_btn)
            kbd_group.add(install_row)

        # Dynamic Keyboard Selection
        kbd_select_row = Adw.ComboRow(title="Active Keyboard")
        kbd_options = self.kbd_mgr.get_available_keyboards()
        kbd_model = Gtk.StringList()
        for opt in kbd_options:
            kbd_model.append(opt["name"])

        kbd_select_row.set_model(kbd_model)

        # Find current index
        current = self.kbd_mgr.get_current_keyboard() # returns 'squeekboard' or 'phosh-osk' or 'unknown'
        # This matching is a bit tricky since we parse dynamic names now.
        # Let's try to match by name.
        found_idx = -1
        for idx, opt in enumerate(kbd_options):
             if current == "squeekboard" and "Squeekboard" in opt["name"]:
                 found_idx = idx
                 break
             elif current == "phosh-osk" and "Stub" in opt["name"]:
                 found_idx = idx
                 break

        if found_idx >= 0:
            kbd_select_row.set_selected(found_idx)

        kbd_select_row.connect("notify::selected", self._on_kbd_changed, kbd_options)
        kbd_group.add(kbd_select_row)

        # Finnish Layout Toggle
        fi_row = Adw.SwitchRow(title="Finnish Layout", subtitle="Install custom Squeekboard layout")
        fi_row.set_active(self.kbd_mgr.is_finnish_layout_installed())
        fi_row.connect("notify::active", self._on_fi_toggled)
        kbd_group.add(fi_row)

        # Environment Section
        env_group = Adw.PreferencesGroup(title="Environment")
        self.add(env_group)

        env_row = Adw.ActionRow(title="Switch Environment")
        env_group.add(env_row)

        staging_btn = Gtk.Button(label="Staging")
        staging_btn.set_valign(Gtk.Align.CENTER)
        staging_btn.connect("clicked", lambda x: run_pkg_cmd("Switching to Staging", self.pkg_mgr.switch_to_staging()))
        env_row.add_suffix(staging_btn)

        prod_btn = Gtk.Button(label="Production")
        prod_btn.set_valign(Gtk.Align.CENTER)
        prod_btn.connect("clicked", lambda x: run_pkg_cmd("Switching to Production", self.pkg_mgr.switch_to_production()))
        env_row.add_suffix(prod_btn)

        # Updates Section
        upg_group = Adw.PreferencesGroup(title="Updates")
        self.add(upg_group)
        upg_row = Adw.ActionRow(title="System Upgrade")
        upg_group.add(upg_row)

        upg_btn = Gtk.Button(label="Upgrade FuriOS")
        upg_btn.add_css_class("suggested-action")
        upg_btn.set_valign(Gtk.Align.CENTER)
        upg_btn.connect("clicked", lambda x: run_pkg_cmd("Upgrading System", self.pkg_mgr.upgrade_system()))
        upg_row.add_suffix(upg_btn)

        # Bat-Mon
        bat_group = Adw.PreferencesGroup(title="Battery Monitor")
        self.add(bat_group)
        bat_row = Adw.ActionRow(title="FLX1s-Bat-Mon", subtitle="Install custom battery monitor")
        bat_group.add(bat_row)

        bat_btn = Gtk.Button(label="Install")
        bat_btn.set_valign(Gtk.Align.CENTER)
        bat_btn.connect("clicked", self._install_bat_mon)
        bat_row.add_suffix(bat_btn)

        # Branchy
        branchy_group = Adw.PreferencesGroup(title="Experimental")
        self.add(branchy_group)
        branchy_row = Adw.ActionRow(title="Install Branchy App Store")
        branchy_group.add(branchy_row)

        branchy_btn = Gtk.Button(label="Install")
        branchy_btn.set_valign(Gtk.Align.CENTER)
        branchy_btn.connect("clicked", lambda x: run_pkg_cmd("Installing Branchy", self.pkg_mgr.install_branchy()))
        branchy_row.add_suffix(branchy_btn)

        # Security Section
        sec_group = Adw.PreferencesGroup(title="Security")
        self.add(sec_group)

        pass_row = Adw.ActionRow(title="Minimum Password Length")
        sec_group.add(pass_row)

        pass_spin = Gtk.SpinButton.new_with_range(1, 100, 1)
        pass_spin.set_value(1)
        pass_spin.set_valign(Gtk.Align.CENTER)
        pass_row.add_suffix(pass_spin)

        def set_pass_len():
            try:
                length = int(pass_spin.get_value())
                cmd = f"python3 -c \"from tweak_flx1s.system.pam import PamManager; print(PamManager().set_min_password_length({length}))\""
                dlg = ExecutionDialog(self.window, "Setting Password Policy", cmd, as_root=True)
                dlg.present()
            except Exception as e:
                logger.error(f"Failed to set password length: {e}")

        pass_btn = Gtk.Button(label="Apply")
        pass_btn.set_valign(Gtk.Align.CENTER)
        pass_btn.connect("clicked", lambda x: set_pass_len())
        pass_row.add_suffix(pass_btn)

        if get_device_model() == "FuriPhoneFLX1":
            fp_row = Adw.ActionRow(title="Fingerprint Authentication", subtitle="Configure PAM for fingerprint support")
            sec_group.add(fp_row)

            def config_fp():
                try:
                    cmd = "python3 -c \"from tweak_flx1s.system.pam import PamManager; print(PamManager().configure_fingerprint())\""
                    dlg = ExecutionDialog(self.window, "Configuring Fingerprint", cmd, as_root=True)
                    dlg.present()
                except Exception as e:
                    logger.error(f"Failed to configure fingerprint: {e}")

            fp_btn = Gtk.Button(label="Enable")
            fp_btn.set_valign(Gtk.Align.CENTER)
            fp_btn.connect("clicked", lambda x: config_fp())
            fp_row.add_suffix(fp_btn)

    def _on_kbd_changed(self, row, param, options):
        try:
            selected_idx = row.get_selected()
            if selected_idx < len(options):
                 target = options[selected_idx]["path"]
                 cmd = self.kbd_mgr.set_keyboard(target)
                 if cmd:
                     dlg = ExecutionDialog(self.window, "Changing Keyboard", cmd, as_root=True)
                     dlg.present()
        except Exception as e:
            logger.error(f"Failed to change keyboard: {e}")

    def _on_fi_toggled(self, row, param):
        if row.get_active():
            if not self.kbd_mgr.install_finnish_layout():
                 row.set_active(False) # revert on failure
        else:
            self.kbd_mgr.remove_finnish_layout()

    def _install_bat_mon(self, btn):
        # git clone https://gitlab.com/Alaraajavamma/flx1s-bat-mon
        # cd flx1s-bat-mon && sudo apt install ./flx1s-bat-mon*.deb
        cmd = (
            "rm -rf /tmp/flx1s-bat-mon && "
            "git clone https://gitlab.com/Alaraajavamma/flx1s-bat-mon /tmp/flx1s-bat-mon && "
            "cd /tmp/flx1s-bat-mon && "
            "apt install -y ./flx1s-bat-mon*.deb"
        )
        dlg = ExecutionDialog(self.window, "Installing FLX1s-Bat-Mon", cmd, as_root=True)
        dlg.present()
