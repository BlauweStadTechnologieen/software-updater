import os
import subprocess
from dotenv_constants import dotenv_constants
from error_handler import global_error_handler
import logging
import settings

logger = logging.getLogger(__name__)

def run_command(cmd: str, cwd:str) -> None:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)

def create_bat_file(cwd: str) -> str | None:
    """
    Creates a 'run.bat' file in the specified current working directory (cwd).
    This file is typically used to run the Python application in the virtual environment.
    Args:
        cwd (str): The current working directory where the 'run.bat' file should be created.
    Returns:
        None
    Notes:
        - If the 'run.bat' file already exists, the function returns without making changes.
        - If an exception occurs during file creation, it logs a custom error message.
    """
    
    global_error_handler("Creating run.bat file", "Now we're creating the run.bat file...")

    bat_file = os.path.join(cwd, "run.bat")

    if os.path.exists(bat_file):
        
        global_error_handler("Creating run.bat file", f"run.bat file already exists in {cwd}")
        
        return bat_file

    try:
        
        with open(bat_file, "w") as f:
            
            f.write("@echo off\n")
            f.write(f'call "{cwd}\\.venv\\Scripts\\activate.bat"\n')
            f.write(f'python "{cwd}\\main.py"\n')  
            f.write("deactivate\n")
        
        return bat_file

    except Exception as e:

        custom_message = f"{e.__class__.__name__} {e}"

        global_error_handler("Creating run.bat file", custom_message)

        return None

def create_env(cwd: str, root_directory:str, personal_access_token:str, organization_owner:str, mql5_root_directory:str) -> str | None:
    """
    Creates a '.env' file in the specified current working directory (cwd).
    This file is typically used to store environment variables, not related to the Python virtual environment itself.
    Args:
        cwd (str): The current working directory where the '.env' file should be created.
    Returns:
        str | None: Full path to '.env' file if it exists or is created successfully; otherwise `None` if an unexpected error occurs.
    Notes:
        - If the '.env' file already exists, the function returns without making changes.
        - If an exception occurs during file creation, it logs a custom error message.
    """

    global_error_handler("Creating .env file", "Now we're creating the .env file...")

    env_file = os.path.join(cwd, ".env")

    if os.path.exists(env_file):
        
        global_error_handler("Creating .env file", f".env file already exists in {cwd}")
        
        return env_file

    try:
        
        with open(env_file, "w") as f:
                        
            f.write("# Environment variables\n# These are mandatory for the application to run\n# Contact Support: hello@bluecitycapital.com\n\n")

            global_error_handler("Creating .env file", f"Creating keys & values in {env_file}...")
            
            dynamic_constants = [

                f"GITHUB_TOKEN={personal_access_token}",
                f"BASE_DIRECTORY={root_directory}",
                f"GITHUB_USERNAME={organization_owner}",
                f"PARENT_DIRECTORY={mql5_root_directory}",

            ]

            for value in dynamic_constants:

                f.write(value + "\n")

            for key, value in dotenv_constants.items():
                
                f.write(f"{key}='{value}'\n")

            global_error_handler("Creating .env file", f".env file created in {cwd}")

            return env_file

    except Exception as e:

        custom_message = f"{e.__class__.__name__} {e}"

        global_error_handler("Creating .env file", custom_message)

        return None
    
def create_requirements_file(cwd:str) -> str | None:
    """
    Create a `requirements.txt` file in the provided working directory if it does not already exist.
    This function logs progress via `global_error_handler`, checks for an existing
    requirements file, and if missing, writes a default file containing:
    - Manual installation instructions
    - A note about `SKIP_DEPENDENCY_INSTALLATION`
    - A cleanup command comment
    - Default dependencies (`python-dotenv`, `requests`)
    Args:
        cwd (str): Absolute or relative path to the target working directory.
    Returns:
        str | None: Full path to `requirements.txt` if it exists or is created
        successfully; otherwise `None` if an unexpected error occurs.
    Raises:
        None: All exceptions are caught internally and reported through
        `global_error_handler`.
    """
    
    dependancies_path =  os.path.join(cwd, settings.requirements_txt_filename)
    
    global_error_handler(f"Creating the {settings.requirements_txt_filename} file", f"Now we're creating the {settings.requirements_txt_filename} file in the {dependancies_path} directory...")

    try:
        
        if os.path.exists(dependancies_path):
            
            # If the requirements.txt file already exists, we log this information and return the path without modifying it.
            
            global_error_handler(f"Creating the {settings.requirements_txt_filename} file", f"{settings.requirements_txt_filename} file already exists in {cwd} as {dependancies_path}")
            
            return dependancies_path
        
        ##########################################################################################################
        # If the requirements.txt file does not exist, we create it and write the necessary default dependencies.#
        ##########################################################################################################
        
        with open(dependancies_path, "w") as f:

            f.write(f"#Contact Support: hello@bluecitycapital.com\n")
            f.write(f"#If you want to test without installing the dependencies, you can set the environment variable SKIP_DEPENDENCY_INSTALLATION to 'true' in your .env file.\n\n")
            f.write(f"#pip freeze > packages.txt && pip uninstall -r packages.txt -y\n")
            f.write("requests\n")
            f.write("python-dotenv\n")

        global_error_handler(f"Creating the {settings.requirements_txt_filename} file", f"{settings.requirements_txt_filename} file successfully created in {cwd} as {dependancies_path}")
        
        return dependancies_path
    
    except Exception as e:

        global_error_handler(f"Unexpected Error with creating a {settings.requirements_txt_filename} file", f"{e}")

        return None

def create_venv(cwd:str) -> str | None:
    """
    Creates a Python virtual environment in the specified directory.

    Args:
        cwd (str): The current working directory where the virtual environment will be created.
    Returns:
        str | None: The path to the virtual environment (.venv) if creation is successful or if it 
                    already exists. Returns None if virtual environment creation fails.
    Raises:
        Handles errors internally and reports them via global_error_handler if venv creation fails.
    Notes:
        - If a virtual environment already exists and is not empty, returns the existing venv path.
        - Creates a .venv directory in the specified working directory.
        - Uses subprocess to execute 'python -m venv .venv' command.
        - On failure, logs error message with stderr and return code.
    """
            
    global_error_handler("Creating Virtual Environment", "First, we're creating the Virtual Environment...")
    
    venv_path = os.path.join(cwd, ".venv")

    if os.path.exists(venv_path) and os.listdir(venv_path):
                
        global_error_handler("Creating Virtual Environment", f"Virtual environment already exists in {cwd} at {venv_path}")
        
        return venv_path

    create_venv = run_command(["python","-m", "venv", ".venv"], cwd)

    if create_venv.returncode != 0:
        
        global_error_handler("Creating Virtual Environment", f"Failed to create virtual environment in {cwd}. Error: {create_venv.stderr} {create_venv.returncode}")
        
        return None
                            
    return create_venv.stdout
    
def create_env_files(cwd:str, root_directory:str, personal_access_token:str, organization_owner:str, mql5_root_directory:str) -> bool:
    
    """
    Scans all subdirectories in a specified base directory and creates a Python virtual environment (.venv)
    in each subdirectory that does not already have one. If a virtual environment already exists, it installs
    dependencies from requirements.txt if present. Handles errors for missing base directory, missing subdirectories,
    and command failures, and prints status messages for each subdirectory.
    """

    try:

        if not create_env(cwd, root_directory, personal_access_token, organization_owner, mql5_root_directory):

            return False

        for fn in (create_venv, create_bat_file):
            
            result = fn(cwd)

            if result is None or result is False:

                global_error_handler("Creating Env Bundle", f"{fn.__name__} failed.")
                
                return False
            
        if not create_requirements_file(cwd):

            return False
               
        global_error_handler("Creating Env Bundle", "All files created successfully.")

        return True
                
    except Exception as e:
        
        custom_message =f"Error in creating env bundle {e}"
        
        global_error_handler("Creating Env Bundle", custom_message)

        return False