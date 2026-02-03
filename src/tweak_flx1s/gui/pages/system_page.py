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
from loguru import logger
from tweak_flx1s.utils import run_command, get_device_model
from tweak_flx1s.gui.dialogs import ExecutionDialog, KeyboardSelectionDialog
from tweak_flx1s.system.package_manager import PackageManager
from tweak_flx1s.system.keyboard import KeyboardManager
from tweak_flx1s.system.phofono import PhofonoManager
from tweak_flx1s.system.wofi import WofiManager

try:
    _
except NameError:
    from gettext import gettext as _

class SystemPage(Adw.PreferencesPage):
    """
    Page for system-level settings.
    Includes: Keyboard, Environment, Updates, Security, Bat-Mon, Phofono, Wofi.
    """
    def __init__(self, window, **kwargs):
        super().__init__(title=_("System"), icon_name="emblem-system-symbolic", **kwargs)
        self.window = window
        self.pkg_mgr = PackageManager()
        self.kbd_mgr = KeyboardManager()
        self.phofono_mgr = PhofonoManager()
        self.wofi_mgr = WofiManager()

        def run_pkg_cmd(title, cmd):
            try:
                dlg = ExecutionDialog(self.window, title, cmd, as_root=True)
                dlg.present()
            except Exception as e:
                logger.error(f"Failed to start execution dialog for {title}: {e}")

        kbd_group = Adw.PreferencesGroup(title=_("Keyboard"))
        self.add(kbd_group)

        if not self.kbd_mgr.check_squeekboard_installed():
            install_row = Adw.ActionRow(title=_("Squeekboard Missing"))
            install_btn = Gtk.Button(label=_("Install"))
            install_btn.set_valign(Gtk.Align.CENTER)
            install_btn.connect("clicked", lambda x: GLib.idle_add(lambda: run_pkg_cmd(_("Installing Squeekboard"), self.kbd_mgr.install_squeekboard()) or False))
            install_row.add_suffix(install_btn)
            kbd_group.add(install_row)

        self.kbd_row = Adw.ActionRow(title=_("Active Keyboard"))
        self.kbd_row.set_title_lines(0)
        self.kbd_row.set_subtitle_lines(0)
        self._update_kbd_subtitle()

        change_kbd_btn = Gtk.Button(label=_("Change Keyboard"))
        change_kbd_btn.set_valign(Gtk.Align.CENTER)
        change_kbd_btn.connect("clicked", self._on_change_keyboard_clicked)
        self.kbd_row.add_suffix(change_kbd_btn)
        kbd_group.add(self.kbd_row)

        fi_row = Adw.SwitchRow(title=_("Finnish Layout"), subtitle=_("Install custom Squeekboard layout"))
        fi_row.set_title_lines(0)
        fi_row.set_subtitle_lines(0)
        fi_row.set_active(self.kbd_mgr.is_finnish_layout_installed())
        fi_row.connect("notify::active", self._on_fi_toggled)
        kbd_group.add(fi_row)

        wofi_group = Adw.PreferencesGroup(title=_("Configuration"))
        self.add(wofi_group)

        wofi_row = Adw.SwitchRow(title=_("Enforce App Wofi Config"), subtitle=_("Use Tweak-FLX1s Wofi style and config"))
        wofi_row.set_title_lines(0)
        wofi_row.set_subtitle_lines(0)
        wofi_row.set_active(self.wofi_mgr.check_config_match())
        wofi_row.connect("notify::active", self._on_wofi_toggled)
        wofi_group.add(wofi_row)

        env_group = Adw.PreferencesGroup(title=_("Environment"))
        self.add(env_group)

        env_row = Adw.ActionRow(title=_("Switch Environment"))
        env_row.set_title_lines(0)
        env_row.set_subtitle_lines(0)
        env_group.add(env_row)

        staging_btn = Gtk.Button(label=_("Staging"))
        staging_btn.set_valign(Gtk.Align.CENTER)
        staging_btn.connect("clicked", lambda x: GLib.idle_add(lambda: run_pkg_cmd(_("Switching to Staging"), self.pkg_mgr.switch_to_staging()) or False))
        env_row.add_suffix(staging_btn)

        prod_btn = Gtk.Button(label=_("Production"))
        prod_btn.set_valign(Gtk.Align.CENTER)
        prod_btn.connect("clicked", lambda x: GLib.idle_add(lambda: run_pkg_cmd(_("Switching to Production"), self.pkg_mgr.switch_to_production()) or False))
        env_row.add_suffix(prod_btn)

        upg_group = Adw.PreferencesGroup(title=_("Updates"))
        self.add(upg_group)
        upg_row = Adw.ActionRow(title=_("System Upgrade"))
        upg_row.set_title_lines(0)
        upg_row.set_subtitle_lines(0)
        upg_group.add(upg_row)

        upg_btn = Gtk.Button(label=_("Upgrade FuriOS"))
        upg_btn.add_css_class("suggested-action")
        upg_btn.set_valign(Gtk.Align.CENTER)
        upg_btn.connect("clicked", lambda x: GLib.idle_add(lambda: run_pkg_cmd(_("Upgrading System"), self.pkg_mgr.upgrade_system()) or False))
        upg_row.add_suffix(upg_btn)

        app_group = Adw.PreferencesGroup(title=_("Applications"))
        self.add(app_group)

        bat_row = Adw.ActionRow(title=_("FLX1s-Bat-Mon"), subtitle=_("Install custom battery monitor"))
        bat_row.set_title_lines(0)
        bat_row.set_subtitle_lines(0)
        app_group.add(bat_row)

        bat_btn = Gtk.Button(label=_("Install"))
        bat_btn.set_valign(Gtk.Align.CENTER)
        bat_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._install_bat_mon(b) or False))
        bat_row.add_suffix(bat_btn)

        self.phofono_row = Adw.ActionRow(title=_("Phofono"), subtitle=_("Alternative Phone and Messages App"))
        self.phofono_row.set_title_lines(0)
        self.phofono_row.set_subtitle_lines(0)
        app_group.add(self.phofono_row)

        self.phofono_btn = Gtk.Button(valign=Gtk.Align.CENTER)
        self.phofono_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_phofono_clicked(b) or False))
        self.phofono_row.add_suffix(self.phofono_btn)
        self._refresh_phofono()

        branchy_row = Adw.ActionRow(title=_("Branchy App Store"))
        branchy_row.set_title_lines(0)
        branchy_row.set_subtitle_lines(0)
        app_group.add(branchy_row)

        branchy_btn = Gtk.Button(label=_("Install"))
        branchy_btn.set_valign(Gtk.Align.CENTER)
        branchy_btn.connect("clicked", lambda x: GLib.idle_add(lambda: run_pkg_cmd(_("Installing Branchy"), self.pkg_mgr.install_branchy()) or False))
        branchy_row.add_suffix(branchy_btn)

        sec_group = Adw.PreferencesGroup(title=_("Security"))
        self.add(sec_group)

        pass_row = Adw.ActionRow(title=_("Minimum Password Length"))
        pass_row.set_title_lines(0)
        pass_row.set_subtitle_lines(0)
        sec_group.add(pass_row)

        pass_spin = Gtk.SpinButton.new_with_range(1, 100, 1)
        pass_spin.set_value(1)
        pass_spin.set_valign(Gtk.Align.CENTER)
        pass_row.add_suffix(pass_spin)

        def set_pass_len():
            try:
                length = int(pass_spin.get_value())
                cmd = f"python3 -c \"from tweak_flx1s.system.pam import PamManager; print(PamManager().set_min_password_length({length}))\""
                dlg = ExecutionDialog(self.window, _("Setting Password Policy"), cmd, as_root=True)
                dlg.present()
            except Exception as e:
                logger.error(f"Failed to set password length: {e}")

        pass_btn = Gtk.Button(label=_("Apply"))
        pass_btn.set_valign(Gtk.Align.CENTER)
        pass_btn.connect("clicked", lambda x: GLib.idle_add(lambda: set_pass_len() or False))
        pass_row.add_suffix(pass_btn)

        if get_device_model() == "FuriPhoneFLX1":
            fp_row = Adw.ActionRow(title=_("Fingerprint Authentication"), subtitle=_("Configure PAM for fingerprint support"))
            fp_row.set_title_lines(0)
            fp_row.set_subtitle_lines(0)
            sec_group.add(fp_row)

            def config_fp():
                try:
                    cmd = "python3 -c \"from tweak_flx1s.system.pam import PamManager; print(PamManager().configure_fingerprint())\""
                    dlg = ExecutionDialog(self.window, _("Configuring Fingerprint"), cmd, as_root=True)
                    dlg.present()
                except Exception as e:
                    logger.error(f"Failed to configure fingerprint: {e}")

            fp_btn = Gtk.Button(label=_("Enable"))
            fp_btn.set_valign(Gtk.Align.CENTER)
            fp_btn.connect("clicked", lambda x: GLib.idle_add(lambda: config_fp() or False))
            fp_row.add_suffix(fp_btn)

    def _update_kbd_subtitle(self):
        current = self.kbd_mgr.get_current_keyboard()
        name = current
        for opt in self.kbd_mgr.get_available_keyboards():
             # Basic fuzzy matching or exact path match
             if opt["path"] == current:
                 name = opt["name"]
                 break
        self.kbd_row.set_subtitle(name)

    def _on_change_keyboard_clicked(self, btn):
        options = self.kbd_mgr.get_available_keyboards()

        def on_select(path):
            cmd = self.kbd_mgr.set_keyboard(path)

            def on_finish(success):
                if success:
                    self._update_kbd_subtitle()
                    restart_cmd = "systemctl --user daemon-reload && systemctl --user restart mobi.Phosh.OSK.service"
                    try:
                        dlg = ExecutionDialog(self.window, _("Restarting Keyboard Service"), restart_cmd, as_root=False)
                        dlg.present()
                    except Exception as e:
                         logger.error(f"Failed to start restart dialog: {e}")

            if cmd:
                dlg = ExecutionDialog(self.window, _("Changing Keyboard"), cmd, as_root=True, on_finish=on_finish)
                dlg.present()

        dlg = KeyboardSelectionDialog(self.window, options, on_select)
        dlg.present()

    def _on_fi_toggled(self, row, param):
        if row.get_active():
            if not self.kbd_mgr.install_finnish_layout():
                 row.set_active(False)
        else:
            self.kbd_mgr.remove_finnish_layout()

    def _on_wofi_toggled(self, row, param):
        if row.get_active():
            self.wofi_mgr.force_install_config()

    def _install_bat_mon(self, btn):
        cmd = (
            "rm -rf /tmp/flx1s-bat-mon && "
            "git clone https://gitlab.com/Alaraajavamma/flx1s-bat-mon /tmp/flx1s-bat-mon && "
            "cd /tmp/flx1s-bat-mon && "
            "apt install -y ./flx1s-bat-mon*.deb"
        )
        dlg = ExecutionDialog(self.window, _("Installing FLX1s-Bat-Mon"), cmd, as_root=True)
        dlg.present()

    def _refresh_phofono(self):
        installed = self.phofono_mgr.check_installed()
        if installed:
            self.phofono_btn.set_label(_("Remove"))
            self.phofono_btn.add_css_class("destructive-action")
            self.phofono_btn.remove_css_class("suggested-action")
            self.phofono_row.set_subtitle(_("Installed"))
        else:
            self.phofono_btn.set_label(_("Install"))
            self.phofono_btn.add_css_class("suggested-action")
            self.phofono_btn.remove_css_class("destructive-action")
            self.phofono_row.set_subtitle(_("Alternative Phone and Messages App"))

    def _on_phofono_clicked(self, btn):
        installed = self.phofono_mgr.check_installed()
        if installed:
            cmd = self.phofono_mgr.get_uninstall_root_cmd()
            def on_finish(success):
                if success:
                    try:
                        self.phofono_mgr.finish_uninstall()
                    except Exception as e:
                        logger.error(f"Finish uninstall failed: {e}")
                    self._refresh_phofono()
            dlg = ExecutionDialog(self.window, _("Removing Phofono"), cmd, as_root=True, on_finish=on_finish)
            dlg.present()
        else:
            try:
                repo_dir = self.phofono_mgr.prepare_install()
                cmd = self.phofono_mgr.get_install_root_cmd(repo_dir)
                def on_finish(success):
                    if success:
                        try:
                            self.phofono_mgr.finish_install()
                        except Exception as e:
                            logger.error(f"Finish install failed: {e}")
                        self._refresh_phofono()
                dlg = ExecutionDialog(self.window, _("Installing Phofono"), cmd, as_root=True, on_finish=on_finish)
                dlg.present()
            except Exception as e:
                logger.error(f"Install setup failed: {e}")
