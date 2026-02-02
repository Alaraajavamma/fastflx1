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
            locale.setlocale(locale.LC_ALL, '')
            logger.info(f"Locale set to: {locale.getlocale()}")
        except locale.Error as e:
            logger.warning(f"Failed to set locale: {e}")

        localedir = LOCALEDIR

        # Fallback for local development
        if not os.path.exists(os.path.join(localedir, "fi", "LC_MESSAGES", f"{DOMAIN}.mo")):
            local_localedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../po"))
            if os.path.exists(local_localedir):
                 # This is tricky because bindtextdomain expects compiled .mo files in specific structure
                 # usually for dev we might not have them compiled.
                 # But let's stick to standard behavior.
                 pass

        logger.info(f"Binding text domain '{DOMAIN}' to '{localedir}'")
        gettext.bindtextdomain(DOMAIN, localedir)
        gettext.textdomain(DOMAIN)

        logger.info("Installing gettext")
        gettext.install(DOMAIN, localedir)

    except Exception as e:
        logger.error(f"Failed to install i18n: {e}")
        builtins._ = lambda x: x
