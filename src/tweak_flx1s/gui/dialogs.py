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
import subprocess
import threading
from loguru import logger
from tweak_flx1s.actions.buttons import PREDEFINED_ACTIONS

try:
    _
except NameError:
    from gettext import gettext as _

class ExecutionDialog(Adw.MessageDialog):
    """Dialog that runs a shell command and shows output."""
    def __init__(self, parent, title, command, as_root=False, on_finish=None):
        super().__init__(heading=title, transient_for=parent)
        self.set_default_size(300, 400)
        self.add_response("close", _("Close"))
        self.set_response_enabled("close", False)
        self.connect("response", self._on_response)
        self.on_finish_callback = on_finish

        if as_root:
            self.command = ["pkexec", "bash", "-c", command]
        else:
            self.command = ["bash", "-c", command]

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(300)
        scrolled.set_vexpand(True)

        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textview.set_monospace(True)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"textview { font-size: 10px; }")
        self.textview.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        scrolled.set_child(self.textview)
        self.set_extra_child(scrolled)

        self.buffer = self.textview.get_buffer()

        self.process = None
        self.thread = threading.Thread(target=self._run_process)
        self.thread.start()

    def _run_process(self):
        try:
            GLib.idle_add(self._append_text, f"Executing: {' '.join(self.command)}\n\n")

            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            while True:
                line = self.process.stdout.readline()
                if not line and self.process.poll() is not None:
                    break
                if line:
                    GLib.idle_add(self._append_text, line)

            rc = self.process.poll()
            GLib.idle_add(self._finish, rc)

        except Exception as e:
            GLib.idle_add(self._append_text, f"\nError: {e}")
            GLib.idle_add(self._finish, -1)

    def _append_text(self, text):
        iter_end = self.buffer.get_end_iter()
        self.buffer.insert(iter_end, text)
        return False

    def _finish(self, rc):
        if rc == 0:
            self.buffer.insert(self.buffer.get_end_iter(), "\n\nSuccess!")
        else:
            self.buffer.insert(self.buffer.get_end_iter(), f"\n\nFailed with code {rc}")
        self.set_response_enabled("close", True)

        if self.on_finish_callback:
            self.on_finish_callback(rc == 0)

        return False

    def _on_response(self, dialog, response_id):
        if response_id == "close":
             GLib.idle_add(lambda: self.close() or False)

class KeyboardSelectionDialog(Adw.Window):
    """Dialog to select a keyboard from available options."""
    def __init__(self, parent, keyboards, on_select):
        super().__init__(transient_for=parent, modal=True, title=_("Select Keyboard"))
        self.set_default_size(350, 400)
        self.keyboards = keyboards
        self.on_select = on_select
        self.selected_path = None

        content = Adw.ToolbarView()
        self.set_content(content)

        header = Adw.HeaderBar()
        content.add_top_bar(header)

        select_btn = Gtk.Button(label=_("Select"))
        select_btn.add_css_class("suggested-action")
        select_btn.connect("clicked", self._on_select_clicked)
        header.pack_start(select_btn)

        cancel_btn = Gtk.Button(label=_("Cancel"))
        cancel_btn.connect("clicked", lambda x: GLib.idle_add(lambda: self.close() or False))
        header.pack_end(cancel_btn)

        list_box = Gtk.ListBox()
        list_box.add_css_class("boxed-list")
        list_box.set_selection_mode(Gtk.SelectionMode.NONE)

        scroll = Gtk.ScrolledWindow()
        scroll.set_child(list_box)

        clamp = Adw.Clamp()
        clamp.set_child(scroll)
        content.set_content(clamp)

        group = None
        for kbd in self.keyboards:
            row = Adw.ActionRow(title=kbd["name"])
            row.set_subtitle(kbd["path"])
            row.set_title_lines(0)
            row.set_subtitle_lines(0)

            chk = Gtk.CheckButton(valign=Gtk.Align.CENTER)
            if group:
                chk.set_group(group)
            else:
                group = chk

            chk.connect("toggled", self._on_toggled, kbd["path"])
            row.add_prefix(chk)
            list_box.append(row)

    def _on_toggled(self, btn, path):
        if btn.get_active():
            self.selected_path = path

    def _on_select_clicked(self, btn):
        if self.selected_path and self.on_select:
            self.on_select(self.selected_path)
        GLib.idle_add(lambda: self.close() or False)

class WofiMenuEditor(Adw.Window):
    """Editor window for Wofi menus."""
    def __init__(self, parent, items, on_save):
        super().__init__(transient_for=parent, modal=True, title=_("Edit Menu"))
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

        save_btn = Gtk.Button(label=_("Save"))
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
            row = Adw.ActionRow(title=item.get("label", _("New Item")))
            row.set_subtitle(item.get("cmd", ""))
            row.set_title_lines(0)
            row.set_subtitle_lines(0)

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
             heading=_("Edit Item") if not is_new else _("Add Item")
        )
        dlg.add_response("cancel", _("Cancel"))
        dlg.add_response("save", _("Save"))
        dlg.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        label_entry = Adw.EntryRow(title=_("Label"))
        label_entry.set_text(item.get("label", ""))
        box.append(label_entry)

        cmd_entry = Adw.EntryRow(title=_("Command"))
        cmd_entry.set_text(item.get("cmd", ""))
        box.append(cmd_entry)

        predefined_grp = Adw.PreferencesGroup(title=_("Predefined"))
        box.append(predefined_grp)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(150)
        scrolled.set_vexpand(True)
        scrolled.set_propagate_natural_height(True)

        radio_list = Gtk.ListBox()
        radio_list.add_css_class("boxed-list")
        scrolled.set_child(radio_list)

        predefined_grp.add(scrolled)

        group = None

        # None option
        none_row = Adw.ActionRow(title=_("None - write it yourself below"))
        none_row.set_title_lines(0)
        none_chk = Gtk.CheckButton(valign=Gtk.Align.CENTER)
        none_chk.set_active(True)
        group = none_chk
        none_row.add_prefix(none_chk)
        radio_list.append(none_row)

        sorted_keys = sorted(PREDEFINED_ACTIONS.keys())
        for key in sorted_keys:
            row = Adw.ActionRow(title=_(key))
            row.set_title_lines(0)
            chk = Gtk.CheckButton(valign=Gtk.Align.CENTER)
            chk.set_group(group)

            if item.get("cmd") == PREDEFINED_ACTIONS[key]:
                 chk.set_active(True)

            def on_toggled(btn, k=key):
                 if btn.get_active():
                      cmd_entry.set_text(PREDEFINED_ACTIONS[k])
                      label_entry.set_text(_(k))

            chk.connect("toggled", on_toggled)
            row.add_prefix(chk)
            radio_list.append(row)

        dlg.set_extra_child(box)

        def response_cb(d, response):
            if response == "save":
                new_item = {"label": label_entry.get_text(), "cmd": cmd_entry.get_text()}
                if is_new:
                    self.items.append(new_item)
                else:
                    self.items[idx] = new_item
                self._refresh_list()
            # Wrap close call
            GLib.idle_add(lambda: d.close() or False)

        dlg.connect("response", response_cb)
        dlg.present()

    def _on_save_clicked(self, btn):
        if self.on_save:
            self.on_save(self.items)
        # Wrap close call
        GLib.idle_add(lambda: self.close() or False)

class ActionSelectionDialog(Adw.Window):
    """Dialog to select an action type and configure it."""
    def __init__(self, parent, current_config, on_save):
        super().__init__(transient_for=parent, modal=True, title=_("Select Action"))
        self.set_default_size(360, 600)
        self.config = current_config.copy()
        self.on_save = on_save

        content = Adw.ToolbarView()
        self.set_content(content)

        header = Adw.HeaderBar()
        content.add_top_bar(header)

        save_btn = Gtk.Button(label=_("Save"))
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self._on_save)
        header.pack_start(save_btn)

        page = Adw.PreferencesPage()
        content.set_content(page)

        type_group = Adw.PreferencesGroup(title=_("Action Type"))
        page.add(type_group)

        cmd_row = Adw.ActionRow(title=_("Custom Command"))
        cmd_row.set_subtitle(_("Execute a shell command"))
        cmd_row.set_title_lines(0)
        cmd_row.set_subtitle_lines(0)
        cmd_chk = Gtk.CheckButton(valign=Gtk.Align.CENTER)
        cmd_chk.set_active(self.config.get("type") == "command" and self.config.get("value") not in PREDEFINED_ACTIONS.values())
        cmd_chk.connect("toggled", self._on_type_toggled, "command")
        cmd_row.add_prefix(cmd_chk)
        type_group.add(cmd_row)
        self.cmd_chk = cmd_chk

        self.cmd_entry = Adw.EntryRow(title=_("Command"))
        self.cmd_entry.set_text(self.config.get("value", "") if self.config.get("type") == "command" else "")
        self.cmd_entry.set_visible(cmd_chk.get_active())
        type_group.add(self.cmd_entry)

        wofi_row = Adw.ActionRow(title=_("Wofi Menu"))
        wofi_row.set_subtitle(_("Show a menu of actions"))
        wofi_row.set_title_lines(0)
        wofi_row.set_subtitle_lines(0)
        wofi_chk = Gtk.CheckButton(valign=Gtk.Align.CENTER)
        wofi_chk.set_group(cmd_chk)
        wofi_chk.set_active(self.config.get("type") == "wofi")
        wofi_chk.connect("toggled", self._on_type_toggled, "wofi")
        wofi_row.add_prefix(wofi_chk)
        type_group.add(wofi_row)
        self.wofi_chk = wofi_chk

        self.edit_menu_btn = Gtk.Button(label=_("Edit Menu"), valign=Gtk.Align.CENTER)
        self.edit_menu_btn.connect("clicked", self._on_edit_menu)
        self.edit_menu_btn.set_visible(wofi_chk.get_active())
        wofi_row.add_suffix(self.edit_menu_btn)

        predef_group = Adw.PreferencesGroup(title=_("Predefined Actions"))
        page.add(predef_group)

        self.predef_chks = {}
        sorted_keys = sorted(PREDEFINED_ACTIONS.keys())
        current_val = self.config.get("value")

        for key in sorted_keys:
            val = PREDEFINED_ACTIONS[key]
            row = Adw.ActionRow(title=_(key))
            row.set_title_lines(0)
            chk = Gtk.CheckButton(valign=Gtk.Align.CENTER)
            chk.set_group(cmd_chk)
            chk.set_active(self.config.get("type") == "command" and current_val == val)
            chk.connect("toggled", self._on_predef_toggled, val)
            row.add_prefix(chk)
            predef_group.add(row)
            self.predef_chks[key] = chk

    def _on_type_toggled(self, chk, type_name):
        if not chk.get_active(): return

        if type_name == "command":
            self.config["type"] = "command"
            self.cmd_entry.set_visible(True)
            self.edit_menu_btn.set_visible(False)
        elif type_name == "wofi":
            self.config["type"] = "wofi"
            self.cmd_entry.set_visible(False)
            self.edit_menu_btn.set_visible(True)

    def _on_predef_toggled(self, chk, cmd_val):
        if not chk.get_active(): return
        self.config["type"] = "command"
        self.config["value"] = cmd_val
        self.cmd_entry.set_visible(False)
        self.edit_menu_btn.set_visible(False)

    def _on_edit_menu(self, btn):
        items = self.config.get("items", [])
        def save_items(new_items):
            self.config["items"] = new_items

        win = WofiMenuEditor(self, items, save_items)
        win.present()

    def _on_save(self, btn):
        if self.cmd_chk.get_active():
            self.config["value"] = self.cmd_entry.get_text()

        if self.on_save:
            self.on_save(self.config)
        # Wrap close call
        GLib.idle_add(lambda: self.close() or False)
