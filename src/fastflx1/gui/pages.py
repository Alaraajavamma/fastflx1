import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
from fastflx1.const import SERVICE_ALARM, SERVICE_GUARD, SERVICE_GESTURES, ICON_APP
from fastflx1.utils import run_command, logger
from fastflx1.gui.dialogs import ExecutionDialog
from fastflx1.gui.weather_dialog import WeatherDialog
from fastflx1.actions.shortcuts import ShortcutsManager
from fastflx1.system.package_manager import PackageManager
from fastflx1.system.andromeda import AndromedaManager
from fastflx1.system.keyboard import KeyboardManager
from fastflx1.system.weather import WeatherManager

class TweaksPage(Adw.PreferencesPage):
    def __init__(self, **kwargs):
        super().__init__(title="Tweaks", icon_name="preferences-system-symbolic", **kwargs)

        group = Adw.PreferencesGroup(title="Background Services")
        self.add(group)

        self._add_service_row(group, "Alarm Volume Fix", "Ensure alarm plays at full volume", SERVICE_ALARM)
        self._add_service_row(group, "Andromeda Guard", "Prevent OSK issues with Andromeda", SERVICE_GUARD)
        self._add_service_row(group, "Gesture Shortcuts", "Enable edge swipe gestures", SERVICE_GESTURES)

    def _add_service_row(self, group, title, subtitle, service_name):
        row = Adw.SwitchRow(title=title, subtitle=subtitle)

        # Check status
        is_active = self._is_active(service_name)
        row.set_active(is_active)

        row.connect("notify::active", self._on_switch_toggled, service_name)
        group.add(row)

    def _is_active(self, service):
        try:
            out = run_command(f"systemctl --user is-enabled {service}", check=False)
            return out == "enabled"
        except:
            return False

    def _on_switch_toggled(self, row, param, service):
        action = "enable --now" if row.get_active() else "disable --now"
        logger.info(f"{action} {service}")
        run_command(f"systemctl --user {action} {service}", check=False)

class ActionsPage(Adw.PreferencesPage):
    def __init__(self, window, **kwargs):
        super().__init__(title="Actions", icon_name="input-gaming-symbolic", **kwargs)
        self.window = window
        self.shortcuts = ShortcutsManager()
        self.andromeda = AndromedaManager()

        # Shortcuts Group
        group = Adw.PreferencesGroup(title="Quick Actions")
        self.add(group)

        # Row with buttons
        row = Adw.ActionRow(title="Shortcuts")
        group.add(row)

        # Helper to add buttons
        def add_btn(icon=None, label=None, callback=None, color_class=None):
            btn = Gtk.Button()
            if icon:
                btn.set_icon_name(icon)
                btn.add_css_class("circular") # Round if icon only
            if label:
                btn.set_label(label)
                # If text only (no icon passed), it is rect by default.

            if color_class:
                btn.add_css_class(color_class)

            btn.set_valign(Gtk.Align.CENTER)
            btn.connect("clicked", lambda x: callback())
            row.add_suffix(btn)

        add_btn(icon="camera-photo-symbolic", callback=self.shortcuts.take_screenshot)
        add_btn(icon="system-shutdown-symbolic", callback=self.shortcuts.kill_active_window, color_class="destructive-action")
        add_btn(icon="flashlight-symbolic", callback=self.shortcuts.toggle_flashlight, color_class="suggested-action")

        # Weather Group
        weather_group = Adw.PreferencesGroup(title="Weather")
        self.add(weather_group)
        weather_row = Adw.ActionRow(title="Add Location")
        weather_group.add(weather_row)

        weather_btn = Gtk.Button(label="Search...")
        weather_btn.set_valign(Gtk.Align.CENTER)
        weather_btn.connect("clicked", self._open_weather_dialog)
        weather_row.add_suffix(weather_btn)

        # Andromeda Group
        andro_group = Adw.PreferencesGroup(title="Andromeda Shared Folders")
        self.add(andro_group)

        mount_row = Adw.ActionRow(title="Mount/Unmount")
        andro_group.add(mount_row)

        def mount_cb():
            cmd = "python3 -c \"from fastflx1.system.andromeda import AndromedaManager; AndromedaManager().mount()\""
            dlg = ExecutionDialog(self.window, "Mounting Shared Folders", cmd, as_root=True)
            dlg.present()

        def unmount_cb():
            cmd = "python3 -c \"from fastflx1.system.andromeda import AndromedaManager; AndromedaManager().unmount()\""
            dlg = ExecutionDialog(self.window, "Unmounting Shared Folders", cmd, as_root=True)
            dlg.present()

        mount_btn = Gtk.Button(label="Mount")
        mount_btn.add_css_class("suggested-action")
        mount_btn.set_valign(Gtk.Align.CENTER)
        mount_btn.connect("clicked", lambda x: mount_cb())
        mount_row.add_suffix(mount_btn)

        unmount_btn = Gtk.Button(label="Unmount")
        unmount_btn.add_css_class("destructive-action")
        unmount_btn.set_valign(Gtk.Align.CENTER)
        unmount_btn.connect("clicked", lambda x: unmount_cb())
        mount_row.add_suffix(unmount_btn)

    def _open_weather_dialog(self, btn):
        dlg = WeatherDialog(self.window)
        dlg.present()

class SystemPage(Adw.PreferencesPage):
    def __init__(self, window, **kwargs):
        super().__init__(title="System", icon_name="emblem-system-symbolic", **kwargs)
        self.window = window
        self.pkg_mgr = PackageManager()
        self.kbd_mgr = KeyboardManager()

        def run_pkg_cmd(title, cmd):
            dlg = ExecutionDialog(self.window, title, cmd, as_root=True)
            dlg.present()

        # Keyboard Config
        kbd_group = Adw.PreferencesGroup(title="Keyboard")
        self.add(kbd_group)

        # Squeekboard install
        if not self.kbd_mgr.check_squeekboard_installed():
            install_row = Adw.ActionRow(title="Squeekboard Missing")
            install_btn = Gtk.Button(label="Install")
            install_btn.set_valign(Gtk.Align.CENTER)
            install_btn.connect("clicked", lambda x: run_pkg_cmd("Installing Squeekboard", self.kbd_mgr.install_squeekboard()))
            install_row.add_suffix(install_btn)
            kbd_group.add(install_row)

        # Keyboard Selection
        kbd_select_row = Adw.ComboRow(title="Default Keyboard")
        kbd_model = Gtk.StringList()
        kbd_model.append("Squeekboard")
        kbd_model.append("Phosh OSK (Stub)")

        kbd_select_row.set_model(kbd_model)

        # Set current selection
        current = self.kbd_mgr.get_current_keyboard()
        if current == "squeekboard":
            kbd_select_row.set_selected(0)
        elif current == "phosh-osk":
            kbd_select_row.set_selected(1)

        kbd_select_row.connect("notify::selected", self._on_kbd_changed)
        kbd_group.add(kbd_select_row)

        # Environment Group
        group = Adw.PreferencesGroup(title="Environment")
        self.add(group)

        # Switch Env
        env_row = Adw.ActionRow(title="Switch Environment")
        group.add(env_row)

        staging_btn = Gtk.Button(label="Staging")
        staging_btn.set_valign(Gtk.Align.CENTER)
        staging_btn.connect("clicked", lambda x: run_pkg_cmd("Switching to Staging", self.pkg_mgr.switch_to_staging()))
        env_row.add_suffix(staging_btn)

        prod_btn = Gtk.Button(label="Production")
        prod_btn.set_valign(Gtk.Align.CENTER)
        prod_btn.connect("clicked", lambda x: run_pkg_cmd("Switching to Production", self.pkg_mgr.switch_to_production()))
        env_row.add_suffix(prod_btn)

        # Upgrade
        upg_group = Adw.PreferencesGroup(title="Updates")
        self.add(upg_group)
        upg_row = Adw.ActionRow(title="System Upgrade")
        upg_group.add(upg_row)

        upg_btn = Gtk.Button(label="Upgrade FuriOS")
        upg_btn.add_css_class("suggested-action")
        upg_btn.set_valign(Gtk.Align.CENTER)
        upg_btn.connect("clicked", lambda x: run_pkg_cmd("Upgrading System", self.pkg_mgr.upgrade_system()))
        upg_row.add_suffix(upg_btn)

        # Branchy
        branchy_group = Adw.PreferencesGroup(title="Experimental")
        self.add(branchy_group)
        branchy_row = Adw.ActionRow(title="Install Branchy App Store")
        branchy_group.add(branchy_row)

        branchy_btn = Gtk.Button(label="Install")
        branchy_btn.set_valign(Gtk.Align.CENTER)
        branchy_btn.connect("clicked", lambda x: run_pkg_cmd("Installing Branchy", self.pkg_mgr.install_branchy()))
        branchy_row.add_suffix(branchy_btn)

    def _on_kbd_changed(self, row, param):
        selected = row.get_selected()
        type_ = "squeekboard" if selected == 0 else "phosh-osk"
        cmd = self.kbd_mgr.set_keyboard(type_)
        if cmd:
            dlg = ExecutionDialog(self.window, "Changing Keyboard", cmd, as_root=True)
            dlg.present()
