from error_handler import global_error_handler
import subprocess
from subprocess import CompletedProcess
import importlib.util
import sys

#print("Script started from:", sys.argv[0])

def run_command(command:list[str], cwd:str = None) -> CompletedProcess | None:
    """
    Executes a shell command in the specified working directory.
    Args:
        command (list[str]): The command and its arguments to execute as a list of strings.
        cwd (str): The working directory in which to run the command.
    Returns:
        CompletedProcess | None: The result of the executed command as a CompletedProcess object,
        or None if the specified directory is invalid.
    Raises:
        Exception: Propagates any exception encountered during command execution after reporting it.
    Notes:
        - If the provided working directory is not valid, the function returns None.
        - Errors encountered during execution are reported using the error_handler before being raised.
    """

    try:
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)

        return result
    
    except Exception as e:

        global_error_handler.error_handler.report_error("Run Command Exception", str(e))

        return None
    
def is_package_installed(package_name:str) -> bool:
    """
    Checks if a Python package is installed by attempting to find its import specification.
    Args:
        package_name (str): The name of the package to check.
    Returns:
        bool: True if the package is installed, False otherwise.
    """

    return importlib.util.find_spec(package_name) is not None

def dependancies_list() -> dict[str, str]:
    """
    Initializes and returns a dictionary mapping package names to their corresponding identifiers.
    Returns:
        dict[str, str]: A dictionary where the keys are package names and the values are their identifiers.
    """
    
    packages = {

        "dotenv"            : "python-detenv",
        "requests"          : "requests",
        "charset-normalizer": "charset-normalizer",
        "idna"              : "idna",
        "urllib3"           : "urllib3",
        "cerfiti"           : "certifi"

    }
    
    return packages

def install_dependencies() -> bool:
    """
    Installs initial Python package dependencies for the initialization of the package.
    
    Subsequent runs of this package - as far as dependancies are converned - will be managed by the virtual environment which will be installed on initialization.
    
    This function checks if specific packages are installed, and if not, attempts to install them using pip.
    If any installation fails or an exception occurs, it logs the error using the global error handler and returns False.
    Returns:
        bool: True if all dependencies are installed successfully, False otherwise.
    Raises:
        Exception: Any error occuring during the installation will be logged to the global_error_handler and returns False.
    """

    try:
            
        packages = dependancies_list()

        for import_name, pip_name in packages.items():
            
            if is_in_venv():

                break
            
            if is_package_installed(import_name): ## Already Installed
                    
                global_error_handler("Dependency Check", f"{import_name} is already installed. Skipping installation....")
                
                continue
               
            run_result = run_command(["pip", "install", pip_name])
            
            if run_result.returncode != 0:

                raise Exception(f"Dependency Installation Failed for {import_name}. Please refer to return code {run_result.returncode}.")
                            
            global_error_handler("Dependency Installation", f"{pip_name} has been successfully installed.")
        
        return True  

    except Exception as e:

        error_subject = "Exception during dependency installation."
        error_message = str(e)

        global_error_handler(error_subject, error_message)

        return False
    
def uninstall_dependencies() -> bool:
    """
    Uninstalls all dependencies listed in the initialized packages & cleans up the resources used on the initialization of a new update.
    This will iterate through the packages returned by `dependancies_list()`, checks if each package is installed,
    and attempts to uninstall it using pip. Handles errors during uninstallation and reports them
    using the global error handler.

    Returns:
        bool: True if all dependencies were uninstalled successfully, False otherwise.
    
    Raises:
        Exception: Handles all exceptions, logs them via the global error handler, and returns False.
    """

    try:

        packages = dependancies_list()

        for import_name, pip_name in packages.items():

            if is_in_venv():

                break
            
            if not is_package_installed(import_name):
                
                continue

            global_error_handler("Dependency Uninstallation", f"Uninstalling {import_name}....")

            run_result = run_command(["pip", "uninstall", "-y", pip_name])

            if run_result.returncode != 0:
                
                raise Exception(f"Dependency Uninstallation Failed for {import_name}. Please refer to return code {run_result.returncode}.")

            global_error_handler("Dependency Uninstallation", f"{import_name} has been successfully cleaned up.")
                    
        return True
    
    except Exception as e:

        error_subject = "Exception During Dependence Uninstallation"
        error_message = str(e)

        global_error_handler(error_subject, error_message)

        return False
    
def is_in_venv() -> bool:

    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        
        global_error_handler("Virtual Environment Detected", "A virtual environment is detected. Skipping initial dependency management and now managing dependencies through the virtual environment....")
        
        return True
    
    else:

        global_error_handler("No Virtual Environment Detected", "No virtual environment detected. Managing dependencies through pip for the current Python environment....")

        return False