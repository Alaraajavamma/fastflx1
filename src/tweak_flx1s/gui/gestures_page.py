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

class TemplateSelectionDialog(Adw.Window):
    """Dialog to select a gesture template."""
    def __init__(self, parent, on_select, used_specs=None):
        super().__init__(transient_for=parent, modal=True, title=_("Select Template"))
        self.set_default_size(350, 500)
        self.on_select = on_select
        self.used_specs = used_specs or []

        content = Adw.ToolbarView()
        self.set_content(content)

        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)
        header.set_show_start_title_buttons(False)
        content.add_top_bar(header)

        close_btn = Gtk.Button(label=_("Close"))
        close_btn.connect("clicked", lambda x: GLib.idle_add(lambda: self.close() or False))
        header.pack_end(close_btn)

        list_box = Gtk.ListBox()
        list_box.add_css_class("boxed-list")
        list_box.set_selection_mode(Gtk.SelectionMode.NONE)

        scroll = Gtk.ScrolledWindow()
        scroll.set_child(list_box)

        clamp = Adw.Clamp()
        clamp.set_child(scroll)
        content.set_content(clamp)

        sorted_specs = sorted(GESTURE_TEMPLATES.keys())
        for key in sorted_specs:
            spec_val = GESTURE_TEMPLATES[key]
            is_used = spec_val in self.used_specs

            row = Adw.ActionRow(title=key)
            row.set_subtitle(spec_val)
            row.set_title_lines(0)
            row.set_subtitle_lines(0)

            if is_used:
                row.set_activatable(False)
                row.set_sensitive(False)
                row.add_suffix(Gtk.Label(label=_("(In Use)")))
            else:
                row.set_activatable(True)
                row.connect("activated", lambda row: GLib.idle_add(lambda: self._on_row_activated(row, key) or False))

            list_box.append(row)

    def _on_row_activated(self, row, key):
        if self.on_select:
             self.on_select(key, GESTURE_TEMPLATES[key])
        GLib.idle_add(lambda: self.close() or False)

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

        spec_row = Adw.EntryRow(title=_("Spec (lisgd)"))
        spec_row.set_text(self.gesture.get("spec", ""))
        gen_group.add(spec_row)
        self.entries["spec"] = spec_row

        tmpl_row = Adw.ActionRow(title=_("Template"))
        tmpl_row.set_subtitle(_("Select from predefined templates"))

        tmpl_btn = Gtk.Button(label=_("Select"), valign=Gtk.Align.CENTER)
        tmpl_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_select_template(b, spec_row) or False))
        tmpl_row.add_suffix(tmpl_btn)
        gen_group.add(tmpl_row)

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

    def _on_select_template(self, btn, entry):
        def on_select(key, val):
             entry.set_text(val)

        dlg = TemplateSelectionDialog(self, on_select, used_specs=self.used_specs)
        dlg.present()

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

    def _on_enable_toggled(self, row, param):
        self.config["enabled"] = row.get_active()
        self.manager.save_config(self.config)
        action = "enable --now" if row.get_active() else "disable --now"
        logger.info(f"{action} {SERVICE_GESTURES}")
        run_command(f"systemctl --user daemon-reload && systemctl --user {action} {SERVICE_GESTURES}", check=False)

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
            edit_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_edit(b, idx) or False))
            row.add_suffix(edit_btn)

            del_btn = Gtk.Button(icon_name="user-trash-symbolic")
            del_btn.add_css_class("flat")
            del_btn.add_css_class("error")
            del_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_delete(b, idx) or False))
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

        """Collect used specs, excluding the current one if editing"""
        used_specs = []
        for i, g in enumerate(gestures):
             if is_new or i != idx:
                  spec = g.get("spec")
                  if spec: used_specs.append(spec)

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
