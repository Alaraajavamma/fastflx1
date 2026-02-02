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

import gettext
import os
import locale
import builtins
from loguru import logger

LOCALEDIR = "/usr/share/locale"
DOMAIN = "tweak-flx1s"

def install_i18n():
    """Install i18n support."""
    try:
        try:
            # On some systems, LC_ALL might not be set, try LC_MESSAGES
            locale.setlocale(locale.LC_ALL, '')
        except locale.Error:
             try:
                 locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
             except locale.Error:
                 pass

        localedir = LOCALEDIR

        # If running from source, try to find a local 'po' or 'locale' dir
        # But 'gettext' really wants compiled .mo files in locale/LANG/LC_MESSAGES/
        # Check if we are in dev mode
        dev_localedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../locale"))
        if os.path.exists(dev_localedir):
            localedir = dev_localedir

        logger.debug(f"Binding text domain '{DOMAIN}' to '{localedir}'")

        # In Python's gettext, install() adds _() to builtins
        # but bindtextdomain is C-level for Gtk.
        # We need BOTH.

        # 1. Python Gettext
        try:
            t = gettext.translation(DOMAIN, localedir, fallback=False)
            t.install()
        except OSError:
             # Fallback
             gettext.install(DOMAIN, localedir)

        # 2. GLib/Gtk Gettext
        # Note: In Python GObject Introspection, you generally don't call bindtextdomain directly
        # unless you use 'locale' module, but Gtk usually picks it up if the ENV vars are set
        # and the .desktop file has the right domain.
        # But explicit bindtextdomain is good practice.

        try:
            import gi
            from gi.repository import GLib, Gtk
            # These might not be exposed directly in all bindings versions,
            # but locale.bindtextdomain exists in Python standard lib
            locale.bindtextdomain(DOMAIN, localedir)
            locale.textdomain(DOMAIN)
        except Exception as e:
            logger.warning(f"Could not bind text domain via locale module: {e}")

    except Exception as e:
        logger.error(f"Failed to install i18n: {e}")
        builtins._ = lambda x: x
