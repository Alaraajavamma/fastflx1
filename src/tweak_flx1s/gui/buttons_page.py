"""
Buttons configuration page.
Copyright (C) 2024 Alaraajavamma <aki@urheiluaki.fi>
License: GPL-3.0-or-later
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio
from tweak_flx1s.actions.buttons import ButtonManager, PREDEFINED_ACTIONS
from tweak_flx1s.utils import logger

class WofiMenuEditor(Adw.Window):
    """Editor window for Wofi menus."""
    def __init__(self, parent, items, on_save):
        super().__init__(transient_for=parent, modal=True, title="Edit Menu")
        self.set_default_size(350, 500)
        self.items = items.copy()
        self.on_save = on_save

        content = Adw.ToolbarView()
        self.set_content(content)

        header = Adw.HeaderBar()
        content.add_top_bar(header)

        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.connect("clicked", self._on_add)
        header.pack_end(add_btn)

        save_btn = Gtk.Button(label="Save")
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self._on_save_clicked)
        header.pack_start(save_btn)

        self.list_box = Gtk.ListBox()
        self.list_box.add_css_class("boxed-list")
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)

        scroll = Gtk.ScrolledWindow()
        scroll.set_child(self.list_box)

        clamp = Adw.Clamp()
        clamp.set_child(scroll)

        content.set_content(clamp)

        self._refresh_list()

    def _refresh_list(self):
        child = self.list_box.get_first_child()
        while child:
            self.list_box.remove(child)
            child = self.list_box.get_first_child()

        for idx, item in enumerate(self.items):
            row = Adw.ActionRow(title=item.get("label", "New Item"))
            row.set_subtitle(item.get("cmd", ""))

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
        if len(self.items) >= 7:
            logger.warning("Max 7 items reached")
            return
        self._show_item_dialog(None)

    def _on_edit(self, btn, idx):
        self._show_item_dialog(idx)

    def _on_delete(self, btn, idx):
        self.items.pop(idx)
        self._refresh_list()

    def _show_item_dialog(self, idx):
        is_new = idx is None
        item = self.items[idx] if not is_new else {"label": "", "cmd": ""}

        dlg = Adw.MessageDialog(
             transient_for=self,
             heading="Edit Item" if not is_new else "Add Item"
        )
        dlg.add_response("cancel", "Cancel")
        dlg.add_response("save", "Save")
        dlg.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        label_entry = Adw.EntryRow(title="Label")
        label_entry.set_text(item.get("label", ""))
        box.append(label_entry)

        cmd_entry = Adw.EntryRow(title="Command")
        cmd_entry.set_text(item.get("cmd", ""))
        box.append(cmd_entry)

        predefined_grp = Adw.PreferencesGroup(title="Predefined")
        box.append(predefined_grp)

        predefined_row = Adw.ComboRow(title="Select Action")
        predefined_model = Gtk.StringList()
        predefined_model.append("Select...")
        sorted_keys = sorted(PREDEFINED_ACTIONS.keys())
        for k in sorted_keys:
            predefined_model.append(k)
        predefined_row.set_model(predefined_model)

        def on_predefined_selected(row, param):
            idx = row.get_selected()
            if idx > 0:
                key = sorted_keys[idx-1]
                cmd = PREDEFINED_ACTIONS[key]
                cmd_entry.set_text(cmd)
                label_entry.set_text(key)

        predefined_row.connect("notify::selected", on_predefined_selected)
        predefined_grp.add(predefined_row)

        dlg.set_extra_child(box)

        def response_cb(d, response):
            if response == "save":
                new_item = {"label": label_entry.get_text(), "cmd": cmd_entry.get_text()}
                if is_new:
                    self.items.append(new_item)
                else:
                    self.items[idx] = new_item
                self._refresh_list()

        dlg.connect("response", response_cb)
        dlg.present()

    def _on_save_clicked(self, btn):
        if self.on_save:
            self.on_save(self.items)
        self.close()

class ButtonsPage(Adw.PreferencesPage):
    """Page for configuring buttons."""
    def __init__(self, **kwargs):
        super().__init__(title="Buttons", icon_name="input-keyboard-symbolic", **kwargs)
        self.manager = ButtonManager()
        self.config = self.manager.config

        self._build_section("short_press", "Short Press")
        self._build_section("double_press", "Double Press")
        self._build_section("long_press", "Long Press")

    def _build_section(self, key, title):
        """Builds the UI section for a button press type."""
        group = Adw.PreferencesGroup(title=title)
        self.add(group)

        locked_conf = self.config.get(key, {}).get("locked", {})
        locked_expander = Adw.ExpanderRow(title="Locked State")
        group.add(locked_expander)

        l_cmd = Adw.EntryRow(title="Command")
        l_cmd.set_text(locked_conf.get("value", ""))
        l_cmd.connect("apply", self._on_cmd_changed, key, "locked")
        locked_expander.add_row(l_cmd)

        self._add_predefined_helper(locked_expander, l_cmd, key, "locked")

        unlocked_conf = self.config.get(key, {}).get("unlocked", {})
        unlocked_expander = Adw.ExpanderRow(title="Unlocked State")
        group.add(unlocked_expander)

        type_model = Gtk.StringList()
        type_model.append("Single Command")
        type_model.append("Wofi Menu")

        type_row = Adw.ComboRow(title="Action Type", model=type_model)
        is_wofi = unlocked_conf.get("type") == "wofi"
        type_row.set_selected(1 if is_wofi else 0)
        type_row.connect("notify::selected", self._on_type_changed, key, "unlocked", unlocked_expander)
        unlocked_expander.add_row(type_row)

        self._refresh_unlocked_ui(key, unlocked_expander, is_wofi)

    def _add_predefined_helper(self, expander, target_entry, key, state):
        combo = Adw.ComboRow(title="Predefined Action")
        model = Gtk.StringList()
        model.append("Select...")
        sorted_keys = sorted(PREDEFINED_ACTIONS.keys())
        for k in sorted_keys:
            model.append(k)
        combo.set_model(model)

        def on_selected(row, param):
            idx = row.get_selected()
            if idx > 0:
                action_key = sorted_keys[idx-1]
                cmd = PREDEFINED_ACTIONS[action_key]
                target_entry.set_text(cmd)
                if key not in self.config: self.config[key] = {}
                if state not in self.config[key]: self.config[key][state] = {}
                self.config[key][state]["value"] = cmd
                if state == "locked":
                    self.config[key][state]["type"] = "command"

                self.manager.save_config(self.config)

        combo.connect("notify::selected", on_selected)
        expander.add_row(combo)
        return combo

    def _on_cmd_changed(self, entry, key, state):
        val = entry.get_text()
        if key not in self.config: self.config[key] = {}
        if state not in self.config[key]: self.config[key][state] = {}

        self.config[key][state]["type"] = "command"
        self.config[key][state]["value"] = val
        self.manager.save_config(self.config)

    def _on_type_changed(self, row, param, key, state, expander):
        is_wofi = (row.get_selected() == 1)

        if key not in self.config: self.config[key] = {}
        if state not in self.config[key]: self.config[key][state] = {}

        self.config[key][state]["type"] = "wofi" if is_wofi else "command"
        self.manager.save_config(self.config)

        self._refresh_unlocked_ui(key, expander, is_wofi)

    def _refresh_unlocked_ui(self, key, expander, is_wofi):
         cmd_row = getattr(self, f"{key}_cmd_row", None)
         predefined_row = getattr(self, f"{key}_predefined_row", None)
         menu_row = getattr(self, f"{key}_menu_row", None)

         if not cmd_row:
             cmd_row = Adw.EntryRow(title="Command")
             cmd_row.set_text(self.config[key]["unlocked"].get("value", ""))
             cmd_row.connect("apply", self._on_cmd_changed, key, "unlocked")
             expander.add_row(cmd_row)
             setattr(self, f"{key}_cmd_row", cmd_row)

             predefined_row = self._add_predefined_helper(expander, cmd_row, key, "unlocked")
             setattr(self, f"{key}_predefined_row", predefined_row)

         if not menu_row:
             menu_row = Adw.ActionRow(title="Menu Items")
             edit_btn = Gtk.Button(label="Edit", valign=Gtk.Align.CENTER)
             edit_btn.connect("clicked", self._on_edit_menu, key)
             menu_row.add_suffix(edit_btn)
             expander.add_row(menu_row)
             setattr(self, f"{key}_menu_row", menu_row)

         cmd_row.set_visible(not is_wofi)
         if predefined_row:
             predefined_row.set_visible(not is_wofi)
         menu_row.set_visible(is_wofi)

    def _on_edit_menu(self, btn, key):
        items = self.config[key]["unlocked"].get("items", [])

        def on_save(new_items):
            self.config[key]["unlocked"]["items"] = new_items
            self.manager.save_config(self.config)

        win = WofiMenuEditor(self.get_root(), items, on_save)
        win.present()
