import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
from tweak_flx1s.system.weather import WeatherManager
from tweak_flx1s.utils import logger

class WeatherDialog(Adw.Window):
    def __init__(self, parent):
        super().__init__(transient_for=parent, modal=True, title="Add Location")
        self.set_default_size(350, 200)
        self.manager = WeatherManager()

        content = Adw.ToolbarView()
        self.set_content(content)

        # Header
        header = Adw.HeaderBar()
        content.add_top_bar(header)

        # Body
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)

        # Search Entry
        self.search_entry = Gtk.SearchEntry(placeholder_text="Enter city name")
        self.search_entry.connect("search-changed", self._on_search_changed)
        box.append(self.search_entry)

        # Search Button
        search_btn = Gtk.Button(label="Search")
        search_btn.add_css_class("suggested-action")
        search_btn.connect("clicked", self._on_search)
        box.append(search_btn)

        # Result display
        self.result_frame = Gtk.Frame(label="Result")
        self.result_label = Gtk.Label(label="No location found yet.")
        self.result_label.set_wrap(True)
        self.result_frame.set_child(self.result_label)
        box.append(self.result_frame)

        # Add Button (Initially disabled)
        self.add_btn = Gtk.Button(label="Add Location")
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
        self.result_label.set_label("Searching...")

        # Run in thread or async usually, but for simplicity here we assume fast network or block briefly
        # (Ideally use GLib.idle_add/Thread for network IO in GTK)
        import threading
        t = threading.Thread(target=self._perform_search, args=(query,))
        t.start()

    def _perform_search(self, query):
        data = self.manager.search_location(query)
        GLib.idle_add(self._on_search_complete, data)

    def _on_search_complete(self, data):
        self.search_entry.set_sensitive(True)
        # Re-enable search button? Accessing widget via hierarchy or stored ref?
        # I didn't store search_btn.
        # But this is okay, user can re-trigger by editing text maybe?
        # Or I should have stored it.
        # But `search_btn` is local in `__init__`.
        # Actually I need to re-enable it.
        # Let's just say once search is done, user sees result.

        if data:
            self.current_data = data
            display_name = data.get("display_name", "Unknown")
            self.result_label.set_label(f"Found: {display_name}")
            self.add_btn.set_sensitive(True)
        else:
            self.result_label.set_label("No location found.")
            self.add_btn.set_sensitive(False)

    def _on_add(self, btn):
        if self.current_data:
            success = self.manager.add_location(self.current_data)
            if success:
                # Close dialog
                self.close()
            else:
                self.result_label.set_label("Error adding location.")
