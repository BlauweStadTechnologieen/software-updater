import hashlib
import subprocess
import os
from error_handler import global_error_handler
import logging

logger = logging.getLogger(__name__) 

def update_requirements(cwd: str, dependancy_filename: str = "requirements.txt") -> bool:
    """
    Install and upgrade project dependencies from a requirements file using a local virtual environment.
    This function expects a virtual environment at ``<cwd>/.venv`` (Windows layout) and:
    - upgrades ``pip`` using the venv's Python executable, then
    - installs/upgrades packages listed in the dependency file (default: ``requirements.txt``).
    The dependency file is used as input only and is never modified.
    Args:
        cwd (str): Project root directory containing the ``.venv`` folder and dependency file.
        dependancy_filename (str, optional): Name of the dependency file located in ``cwd``.
            Defaults to ``"requirements.txt"``.
    Returns:
        bool: ``True`` if pip upgrade and dependency installation both complete successfully;
        otherwise ``False``.
    Side Effects:
        - Executes external subprocess commands for pip operations.
        - Emits status and error messages through ``global_error_handler``.
    Notes:
        - Requires Windows-style virtual environment paths:
          ``.venv/Scripts/python.exe`` and ``.venv/Scripts/pip.exe``.
        - Returns ``False`` if required executables/files are missing or if any subprocess step fails.

    """

    pip_executable    = os.path.join(cwd, ".venv", "Scripts", "pip.exe")
    python_executable = os.path.join(cwd, ".venv", "Scripts", "python.exe")
    requirements_path = os.path.join(cwd, dependancy_filename)

    if not os.path.exists(pip_executable) or not os.path.exists(requirements_path):
        global_error_handler(
            "Dependency Installation Error",
            "Virtual environment or requirements.txt not found.",
            logging_level=logging.ERROR
        )
        return False

    try:
        # Upgrade pip
        subprocess.run(
            [python_executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True,
            text=True
        )

        global_error_handler(
            "PIP Upgrade",
            "Pip version successfully upgraded!",
            logging_level=logging.INFO
        )

    except Exception as e:
        global_error_handler(
            "PIP Upgrade Failed",
            f"{type(e).__name__}: {e}",
            logging_level=logging.ERROR
        )
        return False

    try:
        global_error_handler(
            "Dependency Update",
            "Starting dependency update process...",
            logging_level=logging.INFO
        )

        # Install / upgrade dependencies from file
        subprocess.run(
            [pip_executable, "install", "--upgrade", "-r", requirements_path],
            check=True
        )

        global_error_handler(
            "Dependency Update",
            "Dependencies updated successfully.",
            logging_level=logging.INFO
        )

        return True

    except subprocess.CalledProcessError as e:
        global_error_handler(
            "Dependency Installation Failure",
            f"Failed to install dependencies: {e}",
            logging_level=logging.ERROR
        )
        return False

    except Exception as e:
        global_error_handler(
            "Unexpected Error in Dependency Installation",
            f"{type(e).__name__}: {e}",
            logging_level=logging.ERROR
        )
        return False