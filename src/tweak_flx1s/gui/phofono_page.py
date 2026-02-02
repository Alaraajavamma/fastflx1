"""
Phofono management page.
Copyright (C) 2024 Alaraajavamma <aki@urheiluaki.fi>
License: GPL-3.0-or-later
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
from tweak_flx1s.system.phofono import PhofonoManager
from tweak_flx1s.gui.dialogs import ExecutionDialog
from tweak_flx1s.utils import logger

class PhofonoPage(Adw.PreferencesPage):
    """Page for installing/uninstalling Phofono."""
    def __init__(self, window, **kwargs):
        super().__init__(title="Phofono", icon_name="call-start-symbolic", **kwargs)
        self.window = window
        self.mgr = PhofonoManager()

        group = Adw.PreferencesGroup(title="Phofono Status")
        self.add(group)

        self.status_row = Adw.ActionRow(title="Installation Status")
        group.add(self.status_row)

        self.action_btn = Gtk.Button(valign=Gtk.Align.CENTER)
        self.action_btn.connect("clicked", self._on_action)
        self.status_row.add_suffix(self.action_btn)

        self._refresh()

    def _refresh(self):
        installed = self.mgr.check_installed()
        if installed:
            self.status_row.set_subtitle("Installed")
            self.action_btn.set_label("Uninstall")
            self.action_btn.add_css_class("destructive-action")
            self.action_btn.remove_css_class("suggested-action")
        else:
            self.status_row.set_subtitle("Not Installed")
            self.action_btn.set_label("Install")
            self.action_btn.add_css_class("suggested-action")
            self.action_btn.remove_css_class("destructive-action")

    def _on_action(self, btn):
        installed = self.mgr.check_installed()
        if installed:
            self._do_uninstall()
        else:
            self._do_install()

    def _do_install(self):
        try:
             repo_dir = self.mgr.prepare_install()
             cmd = self.mgr.get_install_root_cmd(repo_dir)

             def on_finish(success):
                 if success:
                     try:
                         self.mgr.finish_install()
                     except Exception as e:
                         logger.error(f"Finish install failed: {e}")
                     self._refresh()

             dlg = ExecutionDialog(self.window, "Installing Phofono", cmd, as_root=True, on_finish=on_finish)
             dlg.present()

        except Exception as e:
             logger.error(f"Install failed: {e}")
             d = Adw.MessageDialog(heading="Error", body=str(e), transient_for=self.window)
             d.add_response("ok", "OK")
             d.present()

    def _do_uninstall(self):
        cmd = self.mgr.get_uninstall_root_cmd()

        def on_finish(success):
             if success:
                 try:
                     self.mgr.finish_uninstall()
                 except Exception as e:
                     logger.error(f"Finish uninstall failed: {e}")
                 self._refresh()

        dlg = ExecutionDialog(self.window, "Uninstalling Phofono", cmd, as_root=True, on_finish=on_finish)
        dlg.present()
