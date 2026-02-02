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
from tweak_flx1s.gui.buttons_page import ButtonsPage
from tweak_flx1s.gui.gestures_page import GesturesPage

try:
    _
except NameError:
    from gettext import gettext as _

class ActionsPage(Adw.PreferencesPage):
    """
    Page for actions configuration.
    Includes: Buttons, Gestures.
    """
    def __init__(self, window, **kwargs):
        super().__init__(title="Actions", icon_name="input-gaming-symbolic", **kwargs)
        self.window = window

        # Note: ButtonsPage and GesturesPage are entire PreferencesPages themselves.
        # Nesting them isn't directly supported by Adw.PreferencesPage structure
        # (you can't add a Page into a Page easily, you add Groups).
        # We need to extract their content or wrap them.

        # Actually, ButtonsPage and GesturesPage in this codebase inherit from Adw.PreferencesPage.
        # If we want to combine them into one "Actions" tab with maybe a switcher or just sequential groups,
        # we need to refactor them to be just a method that returns groups, OR we just use a sub-stack.

        # Given the "3 Tabs" requirement (Tweaks, System, Actions), "Actions" likely contains the configuration
        # for Buttons and Gestures.
        # Let's use a sub-stack (AdwViewStack) inside this page? No, AdwPreferencesPage expects Groups.

        # Approach: We'll modify ButtonsPage/GesturesPage to be just widgets/boxes we can append,
        # OR we just copy their groups here.

        # However, to avoid massive refactoring of those files right now,
        # let's just instantiate them and steal their children (groups).

        self.buttons_page = ButtonsPage()
        self.gestures_page = GesturesPage()

        # We can iterate over children of the pages and reparent them.
        # But wait, AdwPreferencesPage children are not directly exposed as a simple list.
        # We can use `get_first_child` / `get_next_sibling`.

        # Let's try to add a link to open them as subpages?
        # Or just have them as sections.

        # Since the user wants "3 Tabs", and these are big configurations, maybe subpages is cleaner.
        # But let's try to just merge them visually.

        # We'll create a group "Buttons" and put a button to open Buttons config?
        # Or just put all groups here.

        # Let's try reparenting groups.
        # Note: In GTK4 reparenting is done by removing from parent and adding to new parent.

        # Helper to move groups
        def move_groups(source_page):
            # We can't iterate easily while modifying.
            # AdwPreferencesPage doesn't have `get_groups()`. It has children which are likely a ScrolledWindow -> Clamp -> Box -> Groups.
            # This is getting complicated to introspect.

            # Alternative: Re-implement the UI construction here by calling logic.
            # But the logic is inside `__init__` of those classes.
            pass

        # Let's assume for now we use a nested stack switcher for "Buttons | Gestures" inside this page?
        # No, AdwPreferencesPage doesn't support arbitrary widgets well at top level.

        # Let's just link to them.
        # "Configure Buttons >"
        # "Configure Gestures >"
        # This is very Adwaita-like.

        group = Adw.PreferencesGroup(title="Input Configuration")
        self.add(group)

        btn_row = Adw.ActionRow(title="Hardware Buttons", subtitle="Configure short, double, and long press actions")
        btn_nav = Gtk.Button(icon_name="go-next-symbolic")
        btn_nav.add_css_class("flat")
        btn_nav.connect("clicked", self._open_buttons)
        btn_row.add_suffix(btn_nav)
        group.add(btn_row)

        gst_row = Adw.ActionRow(title="Touch Gestures", subtitle="Configure edge swipes and shortcuts")
        gst_nav = Gtk.Button(icon_name="go-next-symbolic")
        gst_nav.add_css_class("flat")
        gst_nav.connect("clicked", self._open_gestures)
        gst_row.add_suffix(gst_nav)
        group.add(gst_row)

    def _open_buttons(self, btn):
        win = Adw.Window(title="Buttons", transient_for=self.window, modal=True)
        win.set_default_size(400, 600)
        content = Adw.ToolbarView()
        win.set_content(content)
        header = Adw.HeaderBar()
        content.add_top_bar(header)
        page = ButtonsPage()
        content.set_content(page)
        win.present()

    def _open_gestures(self, btn):
        win = Adw.Window(title="Gestures", transient_for=self.window, modal=True)
        win.set_default_size(400, 600)
        content = Adw.ToolbarView()
        win.set_content(content)
        header = Adw.HeaderBar()
        content.add_top_bar(header)
        page = GesturesPage()
        content.set_content(page)
        win.present()
