import subprocess
import os

class KeyboardManager:
    def check_squeekboard_installed(self):
        # Check if squeekboard package is installed or the binary exists.
        # "sudo apt install squeekboard" implies it's a deb.
        # fastflx1 is installed as deb, so we can check dpkg or look for binary.
        # dpkg -s squeekboard
        try:
            subprocess.check_call(["dpkg", "-s", "squeekboard"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except:
            return False

    def install_squeekboard(self):
        return "apt install squeekboard -y"

    def get_current_keyboard(self):
        # We need to parse update-alternatives --config Phosh-OSK
        # But --config is interactive. --query is better if available, but --config is standard.
        # `update-alternatives --display Phosh-OSK`
        try:
            out = subprocess.check_output(["update-alternatives", "--display", "Phosh-OSK"], text=True)
            # Output format:
            # Phosh-OSK - auto mode
            #   link best version is ...
            #   current best version is ...
            #   ...
            # /usr/share/applications/sm.puri.Squeekboard.desktop - priority 50
            # ...
            # 'link currently points to ...'

            for line in out.splitlines():
                 if line.startswith(" link currently points to"):
                     path = line.split("to ")[-1].strip()
                     if "Squeekboard" in path:
                         return "squeekboard"
                     elif "Phosh.OskStub" in path:
                         return "phosh-osk"
            return "unknown"
        except:
            return "unknown"

    def set_keyboard(self, keyboard_type):
        # keyboard_type: 'squeekboard' or 'phosh-osk'
        # We need to set the alternative.
        # Path for squeekboard: /usr/share/applications/sm.puri.Squeekboard.desktop
        # Path for phosh-osk: /usr/share/phosh-osk-stub/sm.puri.Phosh.OskStub.desktop

        path = ""
        if keyboard_type == "squeekboard":
             path = "/usr/share/applications/sm.puri.Squeekboard.desktop"
        elif keyboard_type == "phosh-osk":
             path = "/usr/share/phosh-osk-stub/sm.puri.Phosh.OskStub.desktop"

        if path:
            return f"update-alternatives --set Phosh-OSK {path}"
        return ""
