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

import subprocess
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio
from tweak_flx1s.actions.gestures import GesturesManager
from tweak_flx1s.actions.buttons import PREDEFINED_ACTIONS
from tweak_flx1s.gui.dialogs import ActionSelectionDialog
from tweak_flx1s.gui.wizard import GestureWizard
from tweak_flx1s.utils import logger, run_command
from tweak_flx1s.const import SERVICE_GESTURES

try:
    _
except NameError:
    from gettext import gettext as _

class GestureEditor(Adw.Window):
    """Editor for individual gestures."""
    def __init__(self, parent, gesture_data, on_save, used_specs=None):
        super().__init__(transient_for=parent, modal=True, title=_("Edit Gesture"))
        self.set_default_size(400, 600)
        self.gesture = gesture_data.copy()
        self.on_save = on_save
        self.used_specs = used_specs or []
        self.entries = {}
        self.rows = {}

        content = Adw.ToolbarView()
        self.set_content(content)

        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)
        header.set_show_start_title_buttons(False)
        content.add_top_bar(header)

        save_btn = Gtk.Button(label=_("Save"))
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self._on_save_clicked)
        header.pack_start(save_btn)

        close_btn = Gtk.Button(label=_("Close"))
        close_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self.close() or False))
        header.pack_end(close_btn)

        page = Adw.PreferencesPage()
        content.set_content(page)

        gen_group = Adw.PreferencesGroup(title=_("General"))
        page.add(gen_group)

        name_row = Adw.EntryRow(title=_("Name"))
        name_row.set_text(self.gesture.get("name", ""))
        gen_group.add(name_row)
        self.entries["name"] = name_row

        spec_row = Adw.ActionRow(title=_("Trigger Spec"))
        spec_row.set_subtitle(self.gesture.get("spec", _("Not Configured")))

        change_btn = Gtk.Button(label=_("Change"), valign=Gtk.Align.CENTER)
        change_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_change_spec(b, spec_row) or False))
        spec_row.add_suffix(change_btn)
        gen_group.add(spec_row)
        self.rows["spec"] = spec_row

        act_group = Adw.PreferencesGroup(title=_("Actions"))
        page.add(act_group)

        locked_row = Adw.ActionRow(title=_("Locked State"))
        self._update_subtitle(locked_row, "locked")
        l_btn = Gtk.Button(label=_("Edit"), valign=Gtk.Align.CENTER)
        l_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_edit_action(b, "locked") or False))
        locked_row.add_suffix(l_btn)
        act_group.add(locked_row)
        self.rows["locked"] = locked_row

        unlocked_row = Adw.ActionRow(title=_("Unlocked State"))
        self._update_subtitle(unlocked_row, "unlocked")
        u_btn = Gtk.Button(label=_("Edit"), valign=Gtk.Align.CENTER)
        u_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_edit_action(b, "unlocked") or False))
        unlocked_row.add_suffix(u_btn)
        act_group.add(unlocked_row)
        self.rows["unlocked"] = unlocked_row

    def _on_change_spec(self, btn, row):
        def on_complete(new_spec):
            self.gesture["spec"] = new_spec
            row.set_subtitle(new_spec)

        current_spec = self.gesture.get("spec")
        specs_to_exclude = [s for s in self.used_specs if s != current_spec]

        wiz = GestureWizard(self, on_complete, used_specs=specs_to_exclude)
        wiz.present()

    def _update_subtitle(self, row, state_key):
        conf = self.gesture.get(state_key, {})
        atype = conf.get("type", "command")
        val = conf.get("value", "")

        if atype == "wofi":
            row.set_subtitle(_("Wofi Menu"))
        else:
            found = False
            for pname, pcmd in PREDEFINED_ACTIONS.items():
                if pcmd == val:
                    row.set_subtitle(_(pname))
                    found = True
                    break
            if not found:
                row.set_subtitle(val if val else _("No Action"))

    def _on_edit_action(self, btn, state_key):
        if state_key not in self.gesture: self.gesture[state_key] = {}
        conf = self.gesture[state_key]

        def on_save(new_conf):
            self.gesture[state_key] = new_conf
            self._update_subtitle(self.rows[state_key], state_key)

        dlg = ActionSelectionDialog(self, conf, on_save)
        dlg.present()

    def _on_save_clicked(self, btn):
        self.gesture["name"] = self.entries["name"].get_text()

        if not self.gesture.get("spec"):
             dlg = Adw.MessageDialog(
                  transient_for=self,
                  heading=_("Missing Trigger"),
                  body=_("Please configure a gesture trigger before saving."),
             )
             dlg.add_response("ok", _("OK"))
             dlg.present()
             return

        if self.on_save:
            self.on_save(self.gesture)
        GLib.idle_add(lambda: self.close() or False)

class GesturesPage(Adw.PreferencesPage):
    """Page for configuring gestures."""
    def __init__(self, **kwargs):
        super().__init__(title=_("Gestures"), icon_name="input-touchpad-symbolic", **kwargs)
        self.manager = GesturesManager()
        self.config = self.manager.config

        svc_group = Adw.PreferencesGroup(title=_("Service"))
        self.add(svc_group)

        enable_row = Adw.SwitchRow(title=_("Enable Touch Gestures"))

        is_running = self._is_service_running(SERVICE_GESTURES)
        enable_row.set_active(is_running)

        enable_row.connect("notify::active", self._on_enable_toggled)
        svc_group.add(enable_row)

        action_group = Adw.PreferencesGroup(title=_("Actions"))
        self.add(action_group)

        add_row = Adw.ActionRow(title=_("Add New Gesture"))
        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.set_valign(Gtk.Align.CENTER)
        add_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_add(b) or False))
        add_row.add_suffix(add_btn)
        action_group.add(add_row)

        list_group = Adw.PreferencesGroup(title=_("Configured Gestures"))
        self.add(list_group)

        self.list_box = Gtk.ListBox()
        self.list_box.add_css_class("boxed-list")
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        list_group.add(self.list_box)

        self._refresh_list()

    def _is_service_running(self, service):
        """Checks if a service is active (running)."""
        try:
            cmd = ["systemctl", "--user", "is-active", "--quiet", service]
            return subprocess.call(cmd) == 0
        except Exception as e:
            logger.warning(f"Failed to check active status for {service}: {e}")
            return False

    def _on_enable_toggled(self, row, param):
        should_be_active = row.get_active()
        self.config["enabled"] = should_be_active
        self.manager.save_config(self.config)

        try:
            if should_be_active:
                run_command(f"systemctl --user enable {SERVICE_GESTURES}")
                run_command("systemctl --user daemon-reload")
                run_command(f"systemctl --user start {SERVICE_GESTURES}")
            else:
                run_command(f"systemctl --user stop {SERVICE_GESTURES}")
                run_command(f"systemctl --user disable {SERVICE_GESTURES}")
                run_command("systemctl --user daemon-reload")
        except Exception as e:
            logger.error(f"Failed to toggle service {SERVICE_GESTURES}: {e}")

        is_running = self._is_service_running(SERVICE_GESTURES)

        if should_be_active != is_running:
             logger.warning(f"Service {SERVICE_GESTURES} state mismatch. Expected: {should_be_active}, Actual: {is_running}")
             row.set_active(is_running)

    def _refresh_list(self):
        child = self.list_box.get_first_child()
        while child:
            self.list_box.remove(child)
            child = self.list_box.get_first_child()

        gestures = self.config.get("gestures", [])
        for idx, gesture in enumerate(gestures):
            name = gesture.get("name", _("Unnamed Gesture"))
            spec = gesture.get("spec", "")

            row = Adw.ActionRow(title=name, subtitle=spec)
            row.set_title_lines(0)
            row.set_subtitle_lines(0)

            edit_btn = Gtk.Button(icon_name="document-edit-symbolic")
            edit_btn.add_css_class("flat")
            edit_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_edit(b, idx) or False))
            row.add_suffix(edit_btn)

            del_btn = Gtk.Button(icon_name="user-trash-symbolic")
            del_btn.add_css_class("flat")
            del_btn.add_css_class("error")
            del_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_delete(b, idx) or False))
            row.add_suffix(del_btn)

            self.list_box.append(row)

    def _get_used_specs(self, exclude_idx=None):
        gestures = self.config.get("gestures", [])
        specs = []
        for i, g in enumerate(gestures):
            if exclude_idx is None or i != exclude_idx:
                s = g.get("spec")
                if s: specs.append(s)
        return specs

    def _on_add(self, btn):
        def on_wizard_complete(spec):
            new_data = {
                "name": _("New Gesture"),
                "spec": spec,
                "locked": {"type": "command", "value": ""},
                "unlocked": {"type": "command", "value": ""}
            }
            self._show_editor(None, new_data)

        wiz = GestureWizard(self.get_root(), on_wizard_complete, used_specs=self._get_used_specs())
        wiz.present()

    def _on_edit(self, btn, idx):
        self._show_editor(idx)

    def _on_delete(self, btn, idx):
        gestures = self.config.get("gestures", [])
        if 0 <= idx < len(gestures):
            gestures.pop(idx)
            self.manager.save_config(self.config)
            self._refresh_list()
            self._restart_service()

    def _show_editor(self, idx, initial_data=None):
        gestures = self.config.get("gestures", [])
        is_new = idx is None

        if is_new:
            gesture_data = initial_data if initial_data else {}
        else:
            gesture_data = gestures[idx]

        used_specs = self._get_used_specs(exclude_idx=idx)

        def on_save(new_data):
            if is_new:
                gestures.append(new_data)
            else:
                gestures[idx] = new_data
            self.manager.save_config(self.config)
            self._refresh_list()
            self._restart_service()

        win = GestureEditor(self.get_root(), gesture_data, on_save, used_specs=used_specs)
        win.present()

    def _restart_service(self):
        run_command(f"systemctl --user daemon-reload && systemctl --user restart {SERVICE_GESTURES}", check=False)
