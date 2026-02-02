import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
from fastflx1.const import APP_ID, APP_NAME
from fastflx1.gui.window import MainWindow
from fastflx1.utils import logger

class FastFLX1App(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.FLAGS_NONE,
                         **kwargs)
        self.set_resource_base_path("/com/gitlab/fastflx1")

    def do_startup(self):
        Adw.Application.do_startup(self)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)
        win.present()

def start_gui():
    app = FastFLX1App()
    return app.run(sys.argv)
