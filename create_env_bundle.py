import os
import subprocess
from dotenv_constants import dotenv_constants
from init_constants import DIR_ROOT

def run_command(cmd: str, cwd:str) -> None:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)

def get_DIR_ROOT() -> str | None:
    """
    Retrieves the base directory where packages are extracted.
    Returns:
        str: The base directory path.
    Raises:
        KeyError: If the DIR_ROOT constant is not defined.
        FileNotFoundError: If the specified base directory does not exist.
    """
    
    try:
        if not DIR_ROOT:
            
            raise KeyError("You must define a directory where all software packages will be extracted to.")
        
        if not os.path.isdir(DIR_ROOT):
            
            raise FileNotFoundError(f"Base Directory {DIR_ROOT} does not exist.")
        
        print("Root directory is validated...")
        
        return DIR_ROOT
        
    except FileNotFoundError as e:
        
        print(f"Base Directory not found: {e}")
        
        return None

    except KeyError as e:
        
        print(f"Base Directory not specified: {e}")

        return None 
    
    except Exception as e:

        print(f"General Exception Error {e}")

        return None


def create_gitignore(cwd: str) -> str | None:
    """
    Creates a '.gitignore' file in the specified current working directory (cwd).
    This file is used to specify files and directories that should be ignored by Git.
    Args:
        cwd (str): The current working directory where the '.gitignore' file should be created.
    Returns:
        None
    Notes:
        - If the '.gitignore' file already exists, the function returns without making changes.
        - If an exception occurs during file creation, it prints a custom error message.
    """
    
    gitignore_file = os.path.join(cwd, ".gitignore")

    print("Now we are creating the .gitignore file...")

    if os.path.exists(gitignore_file):
        
        print(f".gitignore file already exists in {cwd}")
        
        return gitignore_file

    try:
        
        with open(gitignore_file, "w") as f:
            
            f.write(".venv/\n__pycache__/\n*.pyc\n*.pyo\n*.pyd\n.env\n/run.BAT\n.vscode/\n.idea/\n*.swp\n*.swo\n*.bak\n*.tmp\n*.log\n")
        
        return gitignore_file

    except Exception as e:

        custom_message = f"{e.__class__.__name__} {e}"

        print(custom_message)

        return None

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
        - If an exception occurs during file creation, it prints a custom error message.
    """
    
    print("Next, we are creating run.bat file...")

    bat_file = os.path.join(cwd, "run.bat")

    if os.path.exists(bat_file):
        
        print(f"run.bat file already exists in {cwd}")
        
        return bat_file

    try:
        
        with open(bat_file, "w") as f:
            
            f.write("@echo off\n")
            f.write(f'call "{cwd}\\.venv\\Scripts\\activate.bat"\n')
            f.write(f'python "{cwd}\\<file_to_run>.py"\n')  
            f.write("deactivate\n")
        
        return bat_file

    except Exception as e:

        custom_message = f"{e.__class__.__name__} {e}"

        print(custom_message)

        return None

def create_env(cwd: str) -> str | None:
    """
    Creates a '.env' file in the specified current working directory (cwd).
    This file is typically used to store environment variables, not related to the Python virtual environment itself.
    Args:
        cwd (str): The current working directory where the '.env' file should be created.
    Returns:
        None
    Notes:
        - If the '.env' file already exists, the function returns without making changes.
        - If an exception occurs during file creation, it prints a custom error message.
    """

    print("Now we're creating .env file...")

    env_file = os.path.join(cwd, ".env")

    if os.path.exists(env_file):
        
        print(f".env file already exists in {cwd}")
        
        return env_file

    try:
        
        with open(env_file, "w") as f:
                        
            f.write("# Environment variables\n# These are mandatory for the application to run\n# Contact Support: hello@bluecitycapital.com\n\n")

            print(f"Creating keys & values in {env_file}...")
            
            for key, value in dotenv_constants.items():
                
                f.write(f"{key}='{value}'\n")

        print(f".env file created in {cwd}")

        return env_file

    except Exception as e:

        custom_message = f"{e.__class__.__name__} {e}"

        print(custom_message)

        return None

def create_venv(cwd:str) -> str | None:
    """
    Creates a Python virtual environment in each subdirectory of a specified base directory.
    If a virtual environment already exists, it installs dependencies from requirements.txt if present.
    Handles errors for missing base directory, missing subdirectories, and command failures.
    Prints status messages for each subdirectory.
    """
            
    print("First, we're creaing the Virtual Environment...")
    
    venv_path = os.path.join(cwd, ".venv")

    if os.path.exists(venv_path) and os.listdir(venv_path):
                
        return venv_path

    create_venv = run_command(["python","-m", "venv", ".venv"], cwd)

    if create_venv.returncode != 0:
        
        print(f"Failed to create virtual environment in {cwd}. Error: {create_venv.stderr} {create_venv.returncode}")
        
        return None
                            
    return create_venv.stdout
    
def create_env_files(cwd:str) -> bool:
    
    """
    Scans all subdirectories in a specified base directory and creates a Python virtual environment (.venv)
    in each subdirectory that does not already have one. If a virtual environment already exists, it installs
    dependencies from requirements.txt if present. Handles errors for missing base directory, missing subdirectories,
    and command failures, and prints status messages for each subdirectory.
    """

    try:

        for fn in (create_venv, create_bat_file, create_env, create_gitignore):
            
            result = fn(cwd)

            if result is None or result is False:

                print(f"{fn.__name__} failed.")
                
                return False
               
        print("All files created successfully.")

        return True
                
    except Exception as e:
        
        custom_message =f"Error in creating env bundle {e}"
        
        print(custom_message)

        return False
