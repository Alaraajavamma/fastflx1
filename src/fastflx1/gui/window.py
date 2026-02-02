import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
from fastflx1.gui.pages import TweaksPage, ActionsPage, SystemPage
from fastflx1.const import APP_NAME

class MainWindow(Adw.PreferencesWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title(APP_NAME)
        self.set_default_size(360, 600) # Mobile friendly default

        self.tweaks_page = TweaksPage()
        self.add(self.tweaks_page)

        self.actions_page = ActionsPage(self)
        self.add(self.actions_page)

        # We can add a "System" page for heavy updates
        self.system_page = SystemPage(self)
        self.add(self.system_page)
