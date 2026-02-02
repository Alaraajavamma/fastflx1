import sys
from loguru import logger
import subprocess
import shutil

# Configure logger
logger.remove()
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

def setup_logging():
    """Initializes logging configuration."""
    pass

def run_command(command, check=True):
    """
    Runs a shell command and returns the output.
    'command' can be a string (shell=True) or a list (shell=False).
    """
    use_shell = isinstance(command, str)
    cmd_str = command if use_shell else " ".join(command)

    logger.debug(f"Running command: {cmd_str}")
    try:
        result = subprocess.run(
            command,
            shell=use_shell,
            check=check,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {cmd_str}")
        logger.error(f"Error output: {e.stderr}")
        if check:
            raise
        return None

def check_dependency(name):
    """Checks if a command line tool exists."""
    return shutil.which(name) is not None

def get_device_model():
    """
    Returns the device model based on 'uname -n'.
    Expected values: 'FuriPhoneFLX1', 'FuriPhoneFLX1s', or 'Unknown'.
    """
    try:
        model = run_command("uname -n", check=False)
        if model in ["FuriPhoneFLX1", "FuriPhoneFLX1s"]:
            return model
        return "Unknown"
    except Exception as e:
        logger.error(f"Failed to detect device model: {e}")
        return "Unknown"
