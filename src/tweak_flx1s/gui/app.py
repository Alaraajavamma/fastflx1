"""
Application entry point for GUI.
Copyright (C) 2024 Alaraajavamma <aki@urheiluaki.fi>
License: GPL-3.0-or-later
"""

import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
from tweak_flx1s.const import APP_ID, APP_NAME
from tweak_flx1s.gui.window import MainWindow
from tweak_flx1s.utils import logger

class FastFLX1App(Adw.Application):
    """Main Application class using libadwaita."""
    def __init__(self, **kwargs):
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.FLAGS_NONE,
                         **kwargs)

    def do_startup(self):
        Adw.Application.do_startup(self)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)
        win.present()

def start_gui():
    """Starts the GUI application."""
    app = FastFLX1App()
    return app.run(sys.argv)
