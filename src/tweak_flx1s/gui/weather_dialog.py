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
from tweak_flx1s.system.weather import WeatherManager
from tweak_flx1s.utils import logger
import threading

try:
    _
except NameError:
    from gettext import gettext as _

class WeatherDialog(Adw.Window):
    """Dialog for searching and adding weather locations."""
    def __init__(self, parent):
        super().__init__(transient_for=parent, modal=True, title=_("Add Location"))
        self.set_default_size(350, 200)
        self.manager = WeatherManager()

        content = Adw.ToolbarView()
        self.set_content(content)

        # Header
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)
        header.set_show_start_title_buttons(False)
        content.add_top_bar(header)

        close_btn = Gtk.Button(label=_("Close"))
        close_btn.connect("clicked", lambda b: GLib.idle_add(lambda: self.close() or False))
        header.pack_end(close_btn)

        # Body
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)

        # Search Entry
        self.search_entry = Gtk.SearchEntry(placeholder_text=_("Enter city name"))
        self.search_entry.connect("search-changed", self._on_search_changed)
        box.append(self.search_entry)

        # Search Button
        search_btn = Gtk.Button(label=_("Search"))
        search_btn.add_css_class("suggested-action")
        search_btn.connect("clicked", self._on_search)
        box.append(search_btn)

        # Result display
        self.result_frame = Gtk.Frame(label=_("Result"))
        self.result_label = Gtk.Label(label=_("No location found yet."))
        self.result_label.set_wrap(True)
        self.result_frame.set_child(self.result_label)
        box.append(self.result_frame)

        # Add Button (Initially disabled)
        self.add_btn = Gtk.Button(label=_("Add Location"))
        self.add_btn.set_sensitive(False)
        self.add_btn.connect("clicked", self._on_add)
        box.append(self.add_btn)

        content.set_content(box)

        self.current_data = None

    def _on_search_changed(self, entry):
        self.add_btn.set_sensitive(False)
        self.current_data = None

    def _on_search(self, btn):
        query = self.search_entry.get_text()
        if not query: return

        # Disable interactions while searching
        self.search_entry.set_sensitive(False)
        btn.set_sensitive(False)
        self.result_label.set_label(_("Searching..."))

        t = threading.Thread(target=self._perform_search, args=(query,))
        t.start()

    def _perform_search(self, query):
        data = self.manager.search_location(query)
        GLib.idle_add(self._on_search_complete, data)

    def _on_search_complete(self, data):
        self.search_entry.set_sensitive(True)

        if data:
            self.current_data = data
            display_name = data.get("display_name", "Unknown")
            self.result_label.set_label(f"{_('Found')}: {display_name}")
            self.add_btn.set_sensitive(True)
        else:
            self.result_label.set_label(_("No location found."))
            self.add_btn.set_sensitive(False)

    def _on_add(self, btn):
        if self.current_data:
            success = self.manager.add_location(self.current_data)
            if success:
                # Close dialog
                GLib.idle_add(lambda: self.close() or False)
            else:
                self.result_label.set_label(_("Error adding location."))
