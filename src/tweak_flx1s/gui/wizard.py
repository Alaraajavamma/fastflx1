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
from tweak_flx1s.utils import logger

try:
    _
except NameError:
    from gettext import gettext as _

class GestureWizard(Adw.Window):
    """Wizard to guide the user through creating a gesture spec."""
    def __init__(self, parent, on_complete, used_specs=None, current_spec=None):
        super().__init__(transient_for=parent, modal=True, title=_("New Gesture Wizard"))
        self.set_default_size(500, 600)
        self.on_complete = on_complete
        self.used_specs = used_specs or []
        self.current_spec = current_spec  # For editing existing, if needed later

        self.selected_fingers = "1"
        self.selected_direction = "LR"
        self.selected_edge = "*"
        self.selected_distance = "*"
        self.selected_mode = "R"

        content = Adw.ToolbarView()
        self.set_content(content)

        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)
        header.set_show_start_title_buttons(False)
        content.add_top_bar(header)

        self.cancel_btn = Gtk.Button(label=_("Cancel"))
        self.cancel_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self.close() or False))
        header.pack_start(self.cancel_btn)

        self.next_btn = Gtk.Button(label=_("Next"))
        self.next_btn.add_css_class("suggested-action")
        self.next_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self._on_next() or False))
        header.pack_end(self.next_btn)

        self.carousel = Adw.Carousel()
        self.carousel.set_interactive(False)
        self.carousel.set_allow_scroll_wheel(False)
        self.carousel.set_allow_mouse_drag(False)
        self.carousel.set_allow_long_swipes(False)
        content.set_content(self.carousel)

        self.step_fingers = self._create_step_fingers()
        self.carousel.append(self.step_fingers)

        self.step_direction = self._create_step_direction()
        self.carousel.append(self.step_direction)

        self.step_edge = self._create_step_edge()
        self.carousel.append(self.step_edge)

        self.step_distance = self._create_step_distance()
        self.carousel.append(self.step_distance)

        self.step_mode = self._create_step_mode()
        self.carousel.append(self.step_mode)

    def _create_page(self, title, subtitle):
        page = Adw.PreferencesPage()
        group = Adw.PreferencesGroup()
        group.set_title(title)
        group.set_description(subtitle)
        page.add(group)
        return page, group

    def _create_step_fingers(self):
        page, group = self._create_page(_("Step 1: Fingers"), _("How many fingers used for the gesture?"))

        for val in ["1", "2", "3"]:
            row = Adw.ActionRow(title=val)
            chk = Gtk.CheckButton()
            chk.set_group(self.fingers_group if val != "1" else None)
            if val == "1": self.fingers_group = chk

            chk.set_active(val == "1") # Default
            chk.connect("toggled", self._make_radio_callback(val, "selected_fingers"))
            row.add_prefix(chk)
            row.set_activatable_widget(chk)
            group.add(row)

        return page

    def _create_step_direction(self):
        page, group = self._create_page(_("Step 2: Direction"), _("Which direction is the swipe?"))

        options = [
            ("LR", _("Left -> Right")),
            ("RL", _("Right -> Left")),
            ("UD", _("Up -> Down")),
            ("DU", _("Down -> Up")),
            ("DLUR", _("Down-Left -> Up-Right")),
            ("URDL", _("Up-Right -> Down-Left")),
            ("ULDR", _("Up-Left -> Down-Right")),
            ("DRUL", _("Down-Right -> Up-Left"))
        ]

        first_chk = None
        for code, label in options:
            row = Adw.ActionRow(title=label)
            chk = Gtk.CheckButton()
            chk.set_group(first_chk)
            if not first_chk: first_chk = chk

            chk.set_active(code == "LR")
            chk.connect("toggled", self._make_radio_callback(code, "selected_direction"))
            row.add_prefix(chk)
            row.set_activatable_widget(chk)
            group.add(row)

        return page

    def _create_step_edge(self):
        page, group = self._create_page(_("Step 3: Edge"), _("Where should the gesture start?"))

        options = [
            ("*", _("Anywhere")),
            ("L", _("Left Edge")),
            ("R", _("Right Edge")),
            ("T", _("Top Edge")),
            ("B", _("Bottom Edge")),
            ("TL", _("Top-Left Corner")),
            ("TR", _("Top-Right Corner")),
            ("BL", _("Bottom-Left Corner")),
            ("BR", _("Bottom-Right Corner")),
            ("N", _("None (Middle of screen only)"))
        ]

        first_chk = None
        for code, label in options:
            row = Adw.ActionRow(title=label)
            chk = Gtk.CheckButton()
            chk.set_group(first_chk)
            if not first_chk: first_chk = chk

            chk.set_active(code == "*")
            chk.connect("toggled", self._make_radio_callback(code, "selected_edge"))
            row.add_prefix(chk)
            row.set_activatable_widget(chk)
            group.add(row)

        return page

    def _create_step_distance(self):
        page, group = self._create_page(_("Step 4: Distance"), _("How long should the swipe be?"))

        options = [
            ("*", _("Any Distance")),
            ("S", _("Short")),
            ("M", _("Medium")),
            ("L", _("Large"))
        ]

        first_chk = None
        for code, label in options:
            row = Adw.ActionRow(title=label)
            chk = Gtk.CheckButton()
            chk.set_group(first_chk)
            if not first_chk: first_chk = chk

            chk.set_active(code == "*")
            chk.connect("toggled", self._make_radio_callback(code, "selected_distance"))
            row.add_prefix(chk)
            row.set_activatable_widget(chk)
            group.add(row)

        return page

    def _create_step_mode(self):
        page, group = self._create_page(_("Step 5: Mode"), _("Trigger on press or release?"))

        self.mode_group = Adw.PreferencesGroup() # Container for dynamic rows
        group.add(self.mode_group)

        return page

    def _refresh_mode_step(self):
        """Rebuilds the mode step to check for duplicates."""
        child = self.step_mode.get_first_child()
        # The first child is the wrapper group
        # The wrapper group has a child which is the PreferencesGroup we added
        # Actually, self.step_mode is PreferencesPage.

        # Clear existing rows in our mode_group container logic
        # Adw.PreferencesGroup doesn't have remove_all easily, so we remove children
        # But we don't have a direct reference to children easily in Gtk4 without iterating.

        self.step_mode.remove(self.step_mode.get_first_child())

        group = Adw.PreferencesGroup()
        group.set_title(_("Step 5: Mode"))
        group.set_description(_("Trigger on press or release?"))
        self.step_mode.add(group)

        options = [
            ("R", _("On Release (Recommended)")),
            ("P", _("On Press"))
        ]

        first_chk = None
        valid_selection_exists = False

        for code, label in options:
            test_spec = f"{self.selected_fingers},{self.selected_direction},{self.selected_edge},{self.selected_distance},{code}"
            is_dup = test_spec in self.used_specs

            row = Adw.ActionRow(title=label)

            if is_dup:
                row.set_subtitle(_("Already configured"))
                row.set_sensitive(False)

            chk = Gtk.CheckButton()
            chk.set_group(first_chk)
            if not first_chk: first_chk = chk

            if not is_dup and not valid_selection_exists:
                chk.set_active(True)
                self.selected_mode = code
                valid_selection_exists = True
            elif not is_dup:
                chk.set_active(False)
            else:
                chk.set_active(False)
                chk.set_sensitive(False)

            if not is_dup:
                chk.connect("toggled", self._make_radio_callback(code, "selected_mode"))

            row.add_prefix(chk)
            row.set_activatable_widget(chk)
            group.add(row)

        if not valid_selection_exists:
             self.next_btn.set_sensitive(False)
             lbl = Gtk.Label(label=_("Error: Both Release and Press modes are already configured for this gesture combination."))
             lbl.add_css_class("error")
             group.add(lbl)
        else:
             self.next_btn.set_sensitive(True)

    def _make_radio_callback(self, value, attr_name):
        def _callback(btn):
            if btn.get_active():
                setattr(self, attr_name, value)
                logger.debug(f"Wizard {attr_name} set to {value}")
        return _callback

    def _on_next(self):
        idx = self.carousel.get_position()
        count = self.carousel.get_n_pages()

        if idx < count - 1:
            next_idx = idx + 1
            if next_idx == 4: # Going to Mode step
                self._refresh_mode_step()
                self.next_btn.set_label(_("Finish"))
                self.next_btn.add_css_class("suggested-action")

            self.carousel.scroll_to(self.carousel.get_nth_page(next_idx), True)
        else:
            self._on_finish()

    def _on_finish(self):
        spec = f"{self.selected_fingers},{self.selected_direction},{self.selected_edge},{self.selected_distance},{self.selected_mode}"
        logger.info(f"Wizard completed. Spec: {spec}")
        if self.on_complete:
            self.on_complete(spec)
        GLib.idle_add(lambda: self.close() or False)
