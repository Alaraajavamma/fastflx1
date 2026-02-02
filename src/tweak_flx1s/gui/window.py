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
from gi.repository import Gtk, Adw, Gio, GLib
from loguru import logger
from tweak_flx1s.const import APP_NAME
from tweak_flx1s.gui.pages.info_page import InfoPage
from tweak_flx1s.gui.pages import TweaksPage, ActionsPage, SystemPage
from tweak_flx1s.gui.buttons_page import ButtonsPage
from tweak_flx1s.gui.gestures_page import GesturesPage
from tweak_flx1s.gui.phofono_page import PhofonoPage

try:
    _
except NameError:
    from gettext import gettext as _

class MainWindow(Adw.Window):
    """The main application window."""
    def __init__(self, application=None, **kwargs):
        super().__init__(application=application, **kwargs)
        self.set_title(APP_NAME)
        self.set_default_size(360, 600)

        # Main Layout
        self.overlay = Gtk.Overlay()
        self.set_content(self.overlay)

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.overlay.set_child(main_vbox)

        # Header
        header = Adw.HeaderBar()
        title_lbl = Gtk.Label(label=APP_NAME, css_classes=["title"])
        header.set_title_widget(title_lbl)

        info_btn = Gtk.Button(icon_name="dialog-information-symbolic")
        info_btn.add_css_class("flat")
        info_btn.add_css_class("circular")
        info_btn.connect("clicked", lambda b: InfoPage.show(self))
        header.pack_start(info_btn)

        main_vbox.append(header)

        # Stack
        self.stack = Adw.ViewStack()
        self.stack.set_vexpand(True)
        main_vbox.append(self.stack)

        # Pages
        self.tweaks_page = TweaksPage()
        self.stack.add_titled(self.tweaks_page, "tweaks", _("Tweaks")).set_icon_name("preferences-system-symbolic")

        self.buttons_page = ButtonsPage()
        self.stack.add_titled(self.buttons_page, "buttons", _("Buttons")).set_icon_name("input-keyboard-symbolic")

        self.gestures_page = GesturesPage()
        self.stack.add_titled(self.gestures_page, "gestures", _("Gestures")).set_icon_name("input-touchpad-symbolic")

        self.phofono_page = PhofonoPage(self)
        self.stack.add_titled(self.phofono_page, "phofono", "Phofono").set_icon_name("call-start-symbolic")

        self.actions_page = ActionsPage(self)
        self.stack.add_titled(self.actions_page, "actions", _("Actions")).set_icon_name("input-gaming-symbolic")

        self.system_page = SystemPage(self)
        self.stack.add_titled(self.system_page, "system", _("System")).set_icon_name("emblem-system-symbolic")

        # Switcher
        self.switcher = Adw.ViewSwitcherBar(stack=self.stack, reveal=True)
        main_vbox.append(self.switcher)
