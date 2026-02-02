"""
Main window implementation.
Copyright (C) 2024 Alaraajavamma <aki@urheiluaki.fi>
License: GPL-3.0-or-later
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
from tweak_flx1s.gui.pages import TweaksPage, ActionsPage, SystemPage
from tweak_flx1s.gui.buttons_page import ButtonsPage
from tweak_flx1s.gui.gestures_page import GesturesPage
from tweak_flx1s.gui.phofono_page import PhofonoPage
from tweak_flx1s.const import APP_NAME

class MainWindow(Adw.PreferencesWindow):
    """The main application window."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title(APP_NAME)
        self.set_default_size(360, 600)

        self.tweaks_page = TweaksPage()
        self.add(self.tweaks_page)

        self.buttons_page = ButtonsPage()
        self.add(self.buttons_page)

        self.gestures_page = GesturesPage()
        self.add(self.gestures_page)

        self.phofono_page = PhofonoPage(self)
        self.add(self.phofono_page)

        self.actions_page = ActionsPage(self)
        self.add(self.actions_page)

        self.system_page = SystemPage(self)
        self.add(self.system_page)
