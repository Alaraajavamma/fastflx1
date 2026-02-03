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
from gi.repository import Gtk, Adw, GLib, Gio
from tweak_flx1s.actions.gestures import GesturesManager, GESTURE_TEMPLATES
from tweak_flx1s.actions.buttons import PREDEFINED_ACTIONS
from tweak_flx1s.gui.dialogs import ActionSelectionDialog
from tweak_flx1s.utils import logger, run_command
from tweak_flx1s.const import SERVICE_GESTURES

try:
    _
except NameError:
    from gettext import gettext as _

class GestureEditor(Adw.Window):
    """Editor for individual gestures."""
    def __init__(self, parent, gesture_data, on_save):
        super().__init__(transient_for=parent, modal=True, title=_("Edit Gesture"))
        self.set_default_size(400, 600)
        self.gesture = gesture_data.copy()
        self.on_save = on_save
        self.entries = {}
        self.rows = {}

        content = Adw.ToolbarView()
        self.set_content(content)

        header = Adw.HeaderBar()
        content.add_top_bar(header)

        save_btn = Gtk.Button(label=_("Save"))
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self._on_save_clicked)
        header.pack_start(save_btn)

        page = Adw.PreferencesPage()
        content.set_content(page)

        gen_group = Adw.PreferencesGroup(title=_("General"))
        page.add(gen_group)

        name_row = Adw.EntryRow(title=_("Name"))
        name_row.set_text(self.gesture.get("name", ""))
        gen_group.add(name_row)
        self.entries["name"] = name_row

        spec_row = Adw.EntryRow(title=_("Spec (lisgd)"))
        spec_row.set_text(self.gesture.get("spec", ""))
        gen_group.add(spec_row)
        self.entries["spec"] = spec_row

        spec_combo = Adw.ComboRow(title=_("Templates"))
        spec_model = Gtk.StringList()
        spec_model.append(_("Select Template..."))
        sorted_specs = sorted(GESTURE_TEMPLATES.keys())
        for k in sorted_specs:
            spec_model.append(k)
        spec_combo.set_model(spec_model)
        spec_combo.connect("notify::selected", self._on_template_selected, sorted_specs, spec_row)
        gen_group.add(spec_combo)

        act_group = Adw.PreferencesGroup(title=_("Actions"))
        page.add(act_group)

        locked_row = Adw.ActionRow(title=_("Locked State"))
        self._update_subtitle(locked_row, "locked")
        l_btn = Gtk.Button(label=_("Edit"), valign=Gtk.Align.CENTER)
        l_btn.connect("clicked", self._on_edit_action, "locked")
        locked_row.add_suffix(l_btn)
        act_group.add(locked_row)
        self.rows["locked"] = locked_row

        unlocked_row = Adw.ActionRow(title=_("Unlocked State"))
        self._update_subtitle(unlocked_row, "unlocked")
        u_btn = Gtk.Button(label=_("Edit"), valign=Gtk.Align.CENTER)
        u_btn.connect("clicked", self._on_edit_action, "unlocked")
        unlocked_row.add_suffix(u_btn)
        act_group.add(unlocked_row)
        self.rows["unlocked"] = unlocked_row

    def _on_template_selected(self, row, param, keys, entry):
        idx = row.get_selected()
        if idx > 0:
            key = keys[idx-1]
            val = GESTURE_TEMPLATES[key]
            entry.set_text(val)

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
        self.gesture["spec"] = self.entries["spec"].get_text()

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
        enable_row.set_active(self.config.get("enabled", False))
        enable_row.connect("notify::active", self._on_enable_toggled)
        svc_group.add(enable_row)

        group = Adw.PreferencesGroup(title=_("Configured Gestures"))
        self.add(group)

        add_row = Adw.ActionRow(title=_("Add New Gesture"))
        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.set_valign(Gtk.Align.CENTER)
        add_btn.connect("clicked", self._on_add)
        add_row.add_suffix(add_btn)
        group.add(add_row)

        self.list_box = Gtk.ListBox()
        self.list_box.add_css_class("boxed-list")
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        group.add(self.list_box)

        self._refresh_list()

    def _on_enable_toggled(self, row, param):
        self.config["enabled"] = row.get_active()
        self.manager.save_config(self.config)
        self._restart_service()

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

            edit_btn = Gtk.Button(icon_name="document-edit-symbolic")
            edit_btn.add_css_class("flat")
            edit_btn.connect("clicked", self._on_edit, idx)
            row.add_suffix(edit_btn)

            del_btn = Gtk.Button(icon_name="user-trash-symbolic")
            del_btn.add_css_class("flat")
            del_btn.add_css_class("error")
            del_btn.connect("clicked", self._on_delete, idx)
            row.add_suffix(del_btn)

            self.list_box.append(row)

    def _on_add(self, btn):
        self._show_editor(None)

    def _on_edit(self, btn, idx):
        self._show_editor(idx)

    def _on_delete(self, btn, idx):
        gestures = self.config.get("gestures", [])
        gestures.pop(idx)
        self.manager.save_config(self.config)
        self._refresh_list()
        self._restart_service()

    def _show_editor(self, idx):
        gestures = self.config.get("gestures", [])
        is_new = idx is None
        gesture_data = gestures[idx] if not is_new else {}

        def on_save(new_data):
            if is_new:
                gestures.append(new_data)
            else:
                gestures[idx] = new_data
            self.manager.save_config(self.config)
            self._refresh_list()
            self._restart_service()

        win = GestureEditor(self.get_root(), gesture_data, on_save)
        win.present()

    def _restart_service(self):
        run_command(f"systemctl --user restart {SERVICE_GESTURES}", check=False)
