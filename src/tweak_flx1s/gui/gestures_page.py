"""
Gestures configuration page.
Copyright (C) 2024 Alaraajavamma <aki@urheiluaki.fi>
License: GPL-3.0-or-later
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio
from tweak_flx1s.actions.gestures import GesturesManager
from tweak_flx1s.actions.buttons import PREDEFINED_ACTIONS
from tweak_flx1s.gui.buttons_page import WofiMenuEditor
from tweak_flx1s.utils import logger, run_command
from tweak_flx1s.const import SERVICE_GESTURES

GESTURE_TEMPLATES = {
    "Swipe Left (RL)": "1,RL,*,*,R",
    "Swipe Right (LR)": "1,LR,*,*,R",
    "Swipe Up (BT)": "1,BT,*,*,R",
    "Swipe Down (TB)": "1,TB,*,*,R",
    "Left Edge Swipe Right": "1,LR,L,*,R",
    "Right Edge Swipe Left": "1,RL,R,*,R",
    "Top Edge Swipe Down": "1,TB,T,*,R",
    "Bottom Edge Swipe Up": "1,BT,B,*,R"
}

class GestureEditor(Adw.Window):
    """Editor for individual gestures."""
    def __init__(self, parent, gesture_data, on_save):
        super().__init__(transient_for=parent, modal=True, title="Edit Gesture")
        self.set_default_size(400, 600)
        self.gesture = gesture_data.copy()
        self.on_save = on_save
        self.entries = {}

        content = Adw.ToolbarView()
        self.set_content(content)

        header = Adw.HeaderBar()
        content.add_top_bar(header)

        save_btn = Gtk.Button(label="Save")
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self._on_save_clicked)
        header.pack_start(save_btn)

        page = Adw.PreferencesPage()
        content.set_content(page)

        # General Settings
        gen_group = Adw.PreferencesGroup(title="General")
        page.add(gen_group)

        name_row = Adw.EntryRow(title="Name")
        name_row.set_text(self.gesture.get("name", ""))
        gen_group.add(name_row)
        self.entries["name"] = name_row

        spec_row = Adw.EntryRow(title="Spec (lisgd)")
        spec_row.set_text(self.gesture.get("spec", ""))
        gen_group.add(spec_row)
        self.entries["spec"] = spec_row

        # Spec helper
        spec_combo = Adw.ComboRow(title="Templates")
        spec_model = Gtk.StringList()
        spec_model.append("Select Template...")
        sorted_specs = sorted(GESTURE_TEMPLATES.keys())
        for k in sorted_specs:
            spec_model.append(k)
        spec_combo.set_model(spec_model)
        spec_combo.connect("notify::selected", self._on_template_selected, sorted_specs, spec_row)
        gen_group.add(spec_combo)

        # Locked State
        self._build_action_section(page, "locked", "Locked State")

        # Unlocked State
        self._build_action_section(page, "unlocked", "Unlocked State")

    def _on_template_selected(self, row, param, keys, entry):
        idx = row.get_selected()
        if idx > 0:
            key = keys[idx-1]
            val = GESTURE_TEMPLATES[key]
            entry.set_text(val)

    def _build_action_section(self, page, state_key, title):
        group = Adw.PreferencesGroup(title=title)
        page.add(group)

        conf = self.gesture.get(state_key, {})

        type_model = Gtk.StringList()
        type_model.append("Single Command")
        if state_key == "unlocked":
            type_model.append("Wofi Menu")

        type_row = Adw.ComboRow(title="Action Type", model=type_model)
        is_wofi = conf.get("type") == "wofi" and state_key == "unlocked"
        type_row.set_selected(1 if is_wofi else 0)
        group.add(type_row)
        self.entries[f"{state_key}_type"] = type_row

        cmd_row = Adw.EntryRow(title="Command")
        cmd_row.set_text(conf.get("value", ""))
        group.add(cmd_row)
        self.entries[f"{state_key}_value"] = cmd_row

        predefined_row = Adw.ComboRow(title="Predefined Action")
        p_model = Gtk.StringList()
        p_model.append("Select...")
        sorted_actions = sorted(PREDEFINED_ACTIONS.keys())
        for k in sorted_actions:
            p_model.append(k)
        predefined_row.set_model(p_model)

        def on_predef(row, param):
            idx = row.get_selected()
            if idx > 0:
                k = sorted_actions[idx-1]
                v = PREDEFINED_ACTIONS[k]
                cmd_row.set_text(v)

        predefined_row.connect("notify::selected", on_predef)
        group.add(predefined_row)

        menu_row = Adw.ActionRow(title="Menu Items")
        edit_btn = Gtk.Button(label="Edit", valign=Gtk.Align.CENTER)
        menu_row.add_suffix(edit_btn)
        group.add(menu_row)

        def on_edit_menu(btn):
            items = self.gesture.get(state_key, {}).get("items", [])
            def save_items(new_items):
                if state_key not in self.gesture: self.gesture[state_key] = {}
                self.gesture[state_key]["items"] = new_items
            win = WofiMenuEditor(self, items, save_items)
            win.present()

        edit_btn.connect("clicked", on_edit_menu)

        def update_visibility():
            is_wofi_local = (type_row.get_selected() == 1)
            cmd_row.set_visible(not is_wofi_local)
            predefined_row.set_visible(not is_wofi_local)
            menu_row.set_visible(is_wofi_local)

        type_row.connect("notify::selected", lambda *args: update_visibility())
        update_visibility()

    def _on_save_clicked(self, btn):
        self.gesture["name"] = self.entries["name"].get_text()
        self.gesture["spec"] = self.entries["spec"].get_text()

        for state_key in ["locked", "unlocked"]:
            if state_key not in self.gesture: self.gesture[state_key] = {}

            type_row = self.entries[f"{state_key}_type"]
            is_wofi = (type_row.get_selected() == 1)
            self.gesture[state_key]["type"] = "wofi" if is_wofi else "command"

            cmd_row = self.entries[f"{state_key}_value"]
            self.gesture[state_key]["value"] = cmd_row.get_text()

        if self.on_save:
            self.on_save(self.gesture)
        self.close()

class GesturesPage(Adw.PreferencesPage):
    """Page for configuring gestures."""
    def __init__(self, **kwargs):
        super().__init__(title="Gestures", icon_name="input-touchpad-symbolic", **kwargs)
        self.manager = GesturesManager()
        self.config = self.manager.config

        group = Adw.PreferencesGroup(title="Configured Gestures")
        self.add(group)

        # Add Button
        add_row = Adw.ActionRow(title="Add New Gesture")
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

    def _refresh_list(self):
        child = self.list_box.get_first_child()
        while child:
            self.list_box.remove(child)
            child = self.list_box.get_first_child()

        gestures = self.config.get("gestures", [])
        for idx, gesture in enumerate(gestures):
            name = gesture.get("name", "Unnamed Gesture")
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
