import hashlib
import subprocess
import os
from error_handler import global_error_handler
import logging

logger = logging.getLogger(__name__) 

def check_and_install_new_dependencies(requirements_file:str ="requirements.txt", hash_file=".requirements_hash") -> None:
    """
    Check for changes in requirements file and install dependencies if modifications are detected.
    
    Compares the SHA-256 hash of the requirements file against a stored hash to detect changes.
    If changes are found, installs all dependencies using pip and updates the stored hash.
    
    Args:
        requirements_file (str, optional): Path to the requirements file containing dependency specifications.
            Defaults to "requirements.txt".
        hash_file (str, optional): Path to the file storing the SHA-256 hash of the last processed
            requirements file. Defaults to ".requirements_hash".
    
    Returns:
        None
    
    Side Effects:
        - Executes subprocess commands to install dependencies via pip
        - Creates or updates the hash file with the current requirements file hash
        - Logs status and error messages through global_error_handler
    
    Notes:
        - If the requirements file doesn't exist, logs an INFO message and returns early
        - On installation failure, logs an ERROR message through global_error_handler
        - Installation success updates the stored hash to prevent redundant reinstalls
    """
    def compute_hash(file_path):
        """Computes the hash of a file."""
        with open(file_path, "rb") as f:
            content = f.read()
            return hashlib.sha256(content).hexdigest()

    # Check if requirements.txt exists
    if not os.path.exists(requirements_file):
        custom_message = f"{requirements_file} not found!"
        custom_subject = "Requirements.txt file not found"
        global_error_handler(custom_subject, custom_message, logging_level=logging.INFO)
        return

    # Compute the current hash of requirements.txt
    current_hash = compute_hash(requirements_file)

    # Read the stored hash if it exists
    stored_hash = None
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            stored_hash = f.read().strip()

    # Compare hashes and install dependencies if there are changes
    if current_hash != stored_hash:

        global_error_handler("Dependency Update", "Changes detected in requirements.txt. Starting dependency installation process....", logging_level=logging.INFO)
        
        try:
            subprocess.run(["pip", "install", "-r", requirements_file])
            # Update the stored hash
            with open(hash_file, "w") as f:
                f.write(current_hash)

            global_error_handler("Dependency Update", "Dependencies installed successfully.", logging_level=logging.INFO)
        
        except subprocess.CalledProcessError as e:

            custom_message = f"Failed to install dependencies: {e}"
            custom_subject = "Dependancy installation failure"

            global_error_handler(custom_subject, custom_message, logging_level=logging.ERROR)

            return

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