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
try:
    from tweak_flx1s.gui.password_dialog import PasswordChangeDialog
except ImportError:
    PasswordChangeDialog = None

from tweak_flx1s.system.package_manager import PackageManager
from tweak_flx1s.system.keyboard import KeyboardManager
from tweak_flx1s.system.phofono import PhofonoManager
from tweak_flx1s.system.bat_mon import BatMonManager
from tweak_flx1s.system.wofi import WofiManager
from tweak_flx1s.system.pam import PamManager
from tweak_flx1s.system.debui import DebUiManager

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
        self.bat_mgr = BatMonManager()
        self.wofi_mgr = WofiManager()
        self.pam_mgr = PamManager()
        self.debui_mgr = DebUiManager()

        def run_pkg_cmd(title, cmd):
            try:
                logger.info(f"Starting execution dialog: {title}")
                dlg = ExecutionDialog(self.window, title, cmd, as_root=True)
                dlg.present()
            except Exception as e:
                logger.error(f"Failed to start execution dialog for {title}: {e}")

        kbd_group = Adw.PreferencesGroup(title=_("Keyboard"))
        self.add(kbd_group)

        self.kbd_row = Adw.ActionRow(title=_("Active Keyboard"))
        self.kbd_row.set_title_lines(0)
        self.kbd_row.set_subtitle_lines(0)
        self._update_kbd_subtitle()

        change_kbd_btn = Gtk.Button(label=_("Change Keyboard"))
        change_kbd_btn.set_valign(Gtk.Align.CENTER)
        change_kbd_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_change_keyboard_clicked(b) or False))
        self.kbd_row.add_suffix(change_kbd_btn)
        kbd_group.add(self.kbd_row)

        self.fi_row = Adw.SwitchRow(title=_("Finnish Layout"), subtitle=_("Install custom Squeekboard layout"))
        self.fi_row.set_title_lines(0)
        self.fi_row.set_subtitle_lines(0)
        self.fi_row.set_active(self.kbd_mgr.is_finnish_layout_installed())
        self.fi_row.connect("notify::active", self._on_fi_toggled)
        kbd_group.add(self.fi_row)

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

        self.env_row = Adw.ActionRow(title=_("Current Environment"))
        self.env_row.set_title_lines(0)
        self.env_row.set_subtitle_lines(0)
        env_group.add(self.env_row)

        self.env_btn = Gtk.Button()
        self.env_btn.set_valign(Gtk.Align.CENTER)
        self.env_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_env_clicked(b) or False))
        self.env_row.add_suffix(self.env_btn)
        self._refresh_env_ui()

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

        sq_row = Adw.ActionRow(title=_("Squeekboard"), subtitle=_("On-screen keyboard"))
        sq_row.set_title_lines(0)
        sq_row.set_subtitle_lines(0)
        app_group.add(sq_row)

        self.sq_btn = Gtk.Button()
        self.sq_btn.set_valign(Gtk.Align.CENTER)
        self.sq_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_sq_clicked(b) or False))
        sq_row.add_suffix(self.sq_btn)
        self._refresh_squeekboard_ui()

        bat_row = Adw.ActionRow(title=_("FLX1s-Bat-Mon"), subtitle=_("Install custom battery monitor"))
        bat_row.set_title_lines(0)
        bat_row.set_subtitle_lines(0)
        app_group.add(bat_row)

        self.bat_btn = Gtk.Button(label=_("Install"))
        self.bat_btn.set_valign(Gtk.Align.CENTER)
        self.bat_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_bat_mon_clicked(b) or False))
        bat_row.add_suffix(self.bat_btn)
        self._refresh_bat_mon()

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

        self.branchy_btn = Gtk.Button(label=_("Install"))
        self.branchy_btn.set_valign(Gtk.Align.CENTER)
        self.branchy_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_branchy_clicked(b) or False))
        branchy_row.add_suffix(self.branchy_btn)
        self._refresh_branchy()

        deb_row = Adw.ActionRow(title=_("DebUI"), subtitle=_("Debian Package Installer UI"))
        deb_row.set_title_lines(0)
        deb_row.set_subtitle_lines(0)
        app_group.add(deb_row)

        self.deb_btn = Gtk.Button()
        self.deb_btn.set_valign(Gtk.Align.CENTER)
        self.deb_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_debui_clicked(b) or False))
        deb_row.add_suffix(self.deb_btn)
        self._refresh_debui()

        sec_group = Adw.PreferencesGroup(title=_("Security"))
        self.add(sec_group)

        self.short_pass_row = Adw.SwitchRow(title=_("Enable Shorter Passcodes"), subtitle=_("Allow 1-character passwords"))
        self.short_pass_row.set_title_lines(0)
        self.short_pass_row.set_subtitle_lines(0)
        self.short_pass_row.set_active(self.pam_mgr.check_short_passwords_enabled())
        self.short_pass_row.connect("notify::active", self._on_short_pass_toggled)
        sec_group.add(self.short_pass_row)

        self.change_pass_row = Adw.ActionRow(title=_("Change Password"), subtitle=_("Change current user password"))
        self.change_pass_row.set_title_lines(0)
        self.change_pass_row.set_subtitle_lines(0)

        self.change_pass_row.set_sensitive(self.short_pass_row.get_active())

        change_pass_btn = Gtk.Button(label=_("Change"))
        change_pass_btn.set_valign(Gtk.Align.CENTER)
        change_pass_btn.connect("clicked", lambda x: GLib.idle_add(lambda: self._on_change_password_clicked() or False))
        self.change_pass_row.add_suffix(change_pass_btn)
        sec_group.add(self.change_pass_row)

        if get_device_model() == "FuriPhoneFLX1":
            self.fp_row = Adw.ActionRow(title=_("Fingerprint Authentication"), subtitle=_("Configure PAM for fingerprint support"))
            self.fp_row.set_title_lines(0)
            self.fp_row.set_subtitle_lines(0)
            sec_group.add(self.fp_row)

            self.fp_btn = Gtk.Button(label=_("Enable"))
            self.fp_btn.set_valign(Gtk.Align.CENTER)
            self.fp_btn.connect("clicked", lambda x: GLib.idle_add(lambda: self._on_fp_clicked() or False))
            self.fp_row.add_suffix(self.fp_btn)
            self._refresh_fp_ui()

    def _update_kbd_subtitle(self):
        try:
            current = self.kbd_mgr.get_current_keyboard()
            name = current
            for opt in self.kbd_mgr.get_available_keyboards():
                 if opt["path"] == current:
                     name = opt["name"]
                     break
            self.kbd_row.set_subtitle(name)
        except Exception as e:
            logger.error(f"Failed to update keyboard subtitle: {e}")

    def _on_change_keyboard_clicked(self, btn):
        try:
            logger.info("Opening keyboard selection dialog")
            options = self.kbd_mgr.get_available_keyboards()

            def on_select(path):
                cmd = self.kbd_mgr.set_keyboard(path)

                def on_finish(success):
                    if success:
                        self._update_kbd_subtitle()
                        restart_cmd = "systemctl --user daemon-reload && systemctl --user restart mobi.phosh.OSK"
                        try:
                            logger.info("Restarting keyboard service")
                            dlg = ExecutionDialog(self.window, _("Restarting Keyboard Service"), restart_cmd, as_root=False)
                            dlg.present()
                        except Exception as e:
                             logger.error(f"Failed to start restart dialog: {e}")

                if cmd:
                    dlg = ExecutionDialog(self.window, _("Changing Keyboard"), cmd, as_root=True, on_finish=on_finish)
                    dlg.present()

            dlg = KeyboardSelectionDialog(self.window, options, on_select)
            dlg.present()
        except Exception as e:
            logger.error(f"Failed to handle keyboard change click: {e}")

    def _on_fi_toggled(self, row, param):
        try:
            active = row.get_active()
            logger.info(f"Toggling Finnish layout: {active}")
            if active:
                if not self.kbd_mgr.install_finnish_layout():
                     row.set_active(False)
            else:
                self.kbd_mgr.remove_finnish_layout()
        except Exception as e:
             logger.error(f"Failed to toggle Finnish layout: {e}")

    def _on_wofi_toggled(self, row, param):
        try:
            active = row.get_active()
            logger.info(f"Toggling Wofi config enforcement: {active}")
            if active:
                self.wofi_mgr.force_install_config()
        except Exception as e:
            logger.error(f"Failed to toggle Wofi config: {e}")

    def _refresh_squeekboard_ui(self):
        try:
            installed = self.kbd_mgr.check_squeekboard_installed()
            if installed:
                self.sq_btn.set_label(_("Remove"))
                self.sq_btn.add_css_class("destructive-action")
                self.sq_btn.remove_css_class("suggested-action")
                self.kbd_row.set_sensitive(True)
                self.fi_row.set_sensitive(True)
            else:
                self.sq_btn.set_label(_("Install"))
                self.sq_btn.add_css_class("suggested-action")
                self.sq_btn.remove_css_class("destructive-action")
                self.kbd_row.set_sensitive(False)
                self.fi_row.set_sensitive(False)
        except Exception as e:
             logger.error(f"Failed to refresh squeekboard ui: {e}")

    def _on_sq_clicked(self, btn):
        try:
            installed = self.kbd_mgr.check_squeekboard_installed()
            if installed:
                logger.info("Removing Squeekboard")
                cmd = self.kbd_mgr.get_remove_cmd()
                dlg = ExecutionDialog(self.window, _("Removing Squeekboard"), cmd, as_root=True, on_finish=lambda s: self._refresh_squeekboard_ui())
                dlg.present()
            else:
                logger.info("Installing Squeekboard")
                cmd = self.kbd_mgr.get_install_cmd()
                dlg = ExecutionDialog(self.window, _("Installing Squeekboard"), cmd, as_root=True, on_finish=lambda s: self._refresh_squeekboard_ui())
                dlg.present()
        except Exception as e:
             logger.error(f"Failed to handle Squeekboard click: {e}")

    def _on_short_pass_toggled(self, row, param):
        active = row.get_active()
        self.change_pass_row.set_sensitive(active)

        if active:
            cmd = f"python3 -c \"from tweak_flx1s.system.pam import PamManager; print(PamManager().enable_short_passwords())\""
            dlg = ExecutionDialog(self.window, _("Enabling Shorter Passwords"), cmd, as_root=True)
            dlg.present()
        else:
            cmd = f"python3 -c \"from tweak_flx1s.system.pam import PamManager; print(PamManager().disable_short_passwords())\""
            dlg = ExecutionDialog(self.window, _("Disabling Shorter Passwords"), cmd, as_root=True)
            dlg.present()

    def _on_change_password_clicked(self):
        if PasswordChangeDialog:
            dlg = PasswordChangeDialog(self.window)
            dlg.present()
        else:
            logger.error("PasswordChangeDialog not available (ImportError?)")

    def _refresh_debui(self):
        try:
            installed = self.debui_mgr.check_installed()
            if installed:
                self.deb_btn.set_label(_("Remove"))
                self.deb_btn.add_css_class("destructive-action")
                self.deb_btn.remove_css_class("suggested-action")
            else:
                self.deb_btn.set_label(_("Install"))
                self.deb_btn.add_css_class("suggested-action")
                self.deb_btn.remove_css_class("destructive-action")
        except Exception as e:
            logger.error(f"Failed to refresh DebUI: {e}")

    def _on_debui_clicked(self, btn):
        try:
            installed = self.debui_mgr.check_installed()
            if installed:
                logger.info("Removing DebUI")
                cmd = self.debui_mgr.get_remove_cmd()
                dlg = ExecutionDialog(self.window, _("Removing DebUI"), cmd, as_root=True, on_finish=lambda s: self._refresh_debui())
                dlg.present()
            else:
                logger.info("Installing DebUI")
                cmd = self.debui_mgr.get_install_cmd()
                dlg = ExecutionDialog(self.window, _("Installing DebUI"), cmd, as_root=True, on_finish=lambda s: self._refresh_debui())
                dlg.present()
        except Exception as e:
             logger.error(f"Failed to handle DebUI click: {e}")

    def _refresh_bat_mon(self):
        try:
            installed = self.bat_mgr.check_installed()
            if installed:
                self.bat_btn.set_label(_("Remove"))
                self.bat_btn.add_css_class("destructive-action")
                self.bat_btn.remove_css_class("suggested-action")
            else:
                self.bat_btn.set_label(_("Install"))
                self.bat_btn.add_css_class("suggested-action")
                self.bat_btn.remove_css_class("destructive-action")
        except Exception as e:
            logger.error(f"Failed to refresh Bat Mon status: {e}")

    def _on_bat_mon_clicked(self, btn):
        try:
            installed = self.bat_mgr.check_installed()
            if installed:
                logger.info("Removing FLX1s-Bat-Mon")
                cmd = self.bat_mgr.get_remove_cmd()
                dlg = ExecutionDialog(self.window, _("Removing FLX1s-Bat-Mon"), cmd, as_root=True, on_finish=lambda s: self._refresh_bat_mon())
                dlg.present()
            else:
                logger.info("Installing FLX1s-Bat-Mon")
                cmd = self.bat_mgr.get_install_cmd()
                dlg = ExecutionDialog(self.window, _("Installing FLX1s-Bat-Mon"), cmd, as_root=True, on_finish=lambda s: self._refresh_bat_mon())
                dlg.present()
        except Exception as e:
            logger.error(f"Failed to handle bat mon click: {e}")

    def _refresh_fp_ui(self):
        try:
            enabled = self.pam_mgr.check_fingerprint_status()
            if enabled:
                self.fp_btn.set_label(_("Remove"))
                self.fp_btn.add_css_class("destructive-action")
                self.fp_btn.remove_css_class("suggested-action")
                self.fp_row.set_subtitle(_("Fingerprint is enabled"))
            else:
                self.fp_btn.set_label(_("Enable"))
                self.fp_btn.add_css_class("suggested-action")
                self.fp_btn.remove_css_class("destructive-action")
                self.fp_row.set_subtitle(_("Configure PAM for fingerprint support"))
        except Exception as e:
            logger.error(f"Failed to refresh FP UI: {e}")

    def _on_fp_clicked(self):
        try:
            enabled = self.pam_mgr.check_fingerprint_status()
            if enabled:
                 cmd = "python3 -c \"from tweak_flx1s.system.pam import PamManager; print(PamManager().remove_fingerprint_configuration())\""
                 title = _("Removing Fingerprint")
            else:
                 cmd = "python3 -c \"from tweak_flx1s.system.pam import PamManager; print(PamManager().configure_fingerprint())\""
                 title = _("Configuring Fingerprint")

            def on_finish(success):
                if success: self._refresh_fp_ui()

            dlg = ExecutionDialog(self.window, title, cmd, as_root=True, on_finish=on_finish)
            dlg.present()
        except Exception as e:
            logger.error(f"Failed to handle FP click: {e}")

    def _refresh_phofono(self):
        try:
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
        except Exception as e:
            logger.error(f"Failed to refresh Phofono status: {e}")

    def _on_phofono_clicked(self, btn):
        try:
            installed = self.phofono_mgr.check_installed()
            if installed:
                logger.info("Removing Phofono")
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
                logger.info("Installing Phofono")
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
        except Exception as e:
            logger.error(f"Failed to handle Phofono click: {e}")

    def _refresh_branchy(self):
        try:
            installed = self.pkg_mgr.check_package_installed("furios-app-branchy")
            if installed:
                self.branchy_btn.set_label(_("Remove"))
                self.branchy_btn.add_css_class("destructive-action")
                self.branchy_btn.remove_css_class("suggested-action")
            else:
                self.branchy_btn.set_label(_("Install"))
                self.branchy_btn.add_css_class("suggested-action")
                self.branchy_btn.remove_css_class("destructive-action")
        except Exception as e:
            logger.error(f"Failed to refresh Branchy status: {e}")

    def _on_branchy_clicked(self, btn):
        try:
            installed = self.pkg_mgr.check_package_installed("furios-app-branchy")
            if installed:
                logger.info("Removing Branchy")
                cmd = "apt remove -y furios-app-branchy"
                dlg = ExecutionDialog(self.window, _("Removing Branchy"), cmd, as_root=True, on_finish=lambda s: self._refresh_branchy())
                dlg.present()
            else:
                logger.info("Installing Branchy")
                cmd = self.pkg_mgr.install_branchy()
                dlg = ExecutionDialog(self.window, _("Installing Branchy"), cmd, as_root=True, on_finish=lambda s: self._refresh_branchy())
                dlg.present()
        except Exception as e:
            logger.error(f"Failed to handle Branchy click: {e}")

    def _refresh_env_ui(self):
        try:
            is_staging = self.pkg_mgr.check_is_staging()
            if is_staging:
                self.env_row.set_subtitle(_("Staging"))
                self.env_btn.set_label(_("Switch to Production"))
                self.env_btn.add_css_class("suggested-action")
                self.env_btn.remove_css_class("destructive-action")
            else:
                self.env_row.set_subtitle(_("Production"))
                self.env_btn.set_label(_("Switch to Staging"))
                self.env_btn.add_css_class("destructive-action")
                self.env_btn.remove_css_class("suggested-action")
        except Exception as e:
             logger.error(f"Failed to refresh environment UI: {e}")

    def _on_env_clicked(self, btn):
        try:
            is_staging = self.pkg_mgr.check_is_staging()
            if is_staging:
                logger.info("Switching to Production")
                cmd = self.pkg_mgr.switch_to_production()
                title = _("Switching to Production")
            else:
                logger.info("Switching to Staging")
                cmd = self.pkg_mgr.switch_to_staging()
                title = _("Switching to Staging")

            dlg = ExecutionDialog(self.window, title, cmd, as_root=True, on_finish=lambda s: self._refresh_env_ui())
            dlg.present()
        except Exception as e:
            logger.error(f"Failed to handle environment switch: {e}")
