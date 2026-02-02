import subprocess
from fastflx1.utils import logger, run_command

class PackageManager:
    def switch_to_staging(self):
        cmd = (
            "sudo apt install furios-apt-config-staging furios-apt-config-debian-staging -y && "
            "sudo apt update && "
            "sudo apt install furios-apt-config-krypton-staging -y && "
            "sudo apt update && "
            "sudo apt upgrade -y --allow-downgrades"
        )
        return self._run_in_terminal(cmd)

    def switch_to_production(self):
        cmd = (
            "sudo apt remove furios-apt-config-staging furios-apt-config-debian-staging furios-apt-config-krypton-staging -y && "
            "sudo apt update && "
            "sudo apt upgrade -y --allow-downgrades"
        )
        return self._run_in_terminal(cmd)

    def upgrade_system(self):
        cmd = "sudo apt update && sudo apt upgrade -y --allow-downgrades"
        return self._run_in_terminal(cmd)

    def install_branchy(self):
        # "apt install furios-app-branchy"
        # User requested this specific option
        cmd = "sudo apt install furios-app-branchy -y"
        return self._run_in_terminal(cmd)

    def _run_in_terminal(self, command):
        # The original script uses `kgx -- bash -c ...`
        # We should do the same to show progress to the user, as apt output is interactive/long.
        # "when we show command process make absolutely sure we convert fonts etc tiny enough and wrap them so they are readable also on mobile screen."

        # The user requirement: "Use pkexec for password and then show to progress in GTK4 app"
        # So we shouldn't just pop `kgx`. We should capture output or run it in a way the GUI can display.
        # However, apt requires a PTY often.
        # Running `pkexec apt ...` returns output.
        # Implementing a full terminal emulator in GTK4 is hard without VTE.
        # If I can use VTE (libvte-2.91-gtk4), I can embed a terminal.
        # If not, I can just capture stdout/stderr and show in a TextView.

        # Since I am in the `system` module, I should return the command string or a Popen object?
        # The GUI needs to drive this.
        # So here I will just return the command string for the GUI to execute with pkexec.

        # But wait, `sudo` inside the command string implies we rely on sudo being configured or asking password in terminal.
        # The requirement says "Use pkexec for password".
        # So the command should be `pkexec bash -c 'apt ...'`.

        # I'll expose the raw shell commands here, and let the GUI handle the execution wrapper (pkexec + display).
        return command.replace("sudo ", "") # Strip sudo, let caller handle privilege escalation
