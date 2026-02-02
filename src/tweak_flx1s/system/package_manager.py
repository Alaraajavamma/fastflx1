"""
Package management helpers.
Copyright (C) 2024 Alaraajavamma <aki@urheiluaki.fi>
License: GPL-3.0-or-later
"""

import subprocess
from tweak_flx1s.utils import logger, run_command

class PackageManager:
    """Helper class for package management commands."""

    def switch_to_staging(self):
        """Returns command to switch to staging repositories."""
        cmd = (
            "sudo apt install furios-apt-config-staging furios-apt-config-debian-staging -y && "
            "sudo apt update && "
            "sudo apt install furios-apt-config-krypton-staging -y && "
            "sudo apt update && "
            "sudo apt upgrade -y --allow-downgrades"
        )
        return self._run_in_terminal(cmd)

    def switch_to_production(self):
        """Returns command to switch to production repositories."""
        cmd = (
            "sudo apt remove furios-apt-config-staging furios-apt-config-debian-staging furios-apt-config-krypton-staging -y && "
            "sudo apt update && "
            "sudo apt upgrade -y --allow-downgrades"
        )
        return self._run_in_terminal(cmd)

    def upgrade_system(self):
        """Returns command to upgrade system."""
        cmd = "sudo apt update && sudo apt upgrade -y --allow-downgrades"
        return self._run_in_terminal(cmd)

    def install_branchy(self):
        """Returns command to install furios-app-branchy."""
        cmd = "sudo apt install furios-app-branchy -y"
        return self._run_in_terminal(cmd)

    def _run_in_terminal(self, command):
        """Helper to format command for execution."""
        return command.replace("sudo ", "")
