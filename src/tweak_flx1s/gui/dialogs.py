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
from gi.repository import Gtk, Adw, GLib, Pango
import subprocess
import threading
from tweak_flx1s.utils import logger

class ExecutionDialog(Adw.MessageDialog):
    """Dialog that runs a shell command and shows output."""
    def __init__(self, parent, title, command, as_root=False, on_finish=None):
        super().__init__(heading=title, transient_for=parent)
        self.set_default_size(300, 400)
        self.add_response("close", "Close")
        self.set_response_enabled("close", False)
        self.on_finish_callback = on_finish

        if as_root:
            self.command = ["pkexec", "bash", "-c", command]
        else:
            self.command = ["bash", "-c", command]

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(300)
        scrolled.set_vexpand(True)

        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textview.set_monospace(True)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"textview { font-size: 10px; }")
        self.textview.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        scrolled.set_child(self.textview)
        self.set_extra_child(scrolled)

        self.buffer = self.textview.get_buffer()

        self.process = None
        self.thread = threading.Thread(target=self._run_process)
        self.thread.start()

    def _run_process(self):
        try:
            GLib.idle_add(self._append_text, f"Executing: {' '.join(self.command)}\n\n")

            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            while True:
                line = self.process.stdout.readline()
                if not line and self.process.poll() is not None:
                    break
                if line:
                    GLib.idle_add(self._append_text, line)

            rc = self.process.poll()
            GLib.idle_add(self._finish, rc)

        except Exception as e:
            GLib.idle_add(self._append_text, f"\nError: {e}")
            GLib.idle_add(self._finish, -1)

    def _append_text(self, text):
        iter_end = self.buffer.get_end_iter()
        self.buffer.insert(iter_end, text)
        adj = self.textview.get_parent().get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())
        return False

    def _finish(self, rc):
        if rc == 0:
            self.buffer.insert(self.buffer.get_end_iter(), "\n\nSuccess!")
        else:
            self.buffer.insert(self.buffer.get_end_iter(), f"\n\nFailed with code {rc}")
        self.set_response_enabled("close", True)

        if self.on_finish_callback:
            self.on_finish_callback(rc == 0)

        return False
