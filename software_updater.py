import subprocess
import hashlib
import os
from directories_to_update import directories_to_update
from pathlib import Path
from install_new_dependencies import check_and_install_new_dependencies
from dotenv import load_dotenv

load_dotenv()

BASE_DIRECTORY_ENV = {
    "BASE_DIRECTORY" : os.getenv("BASE_DIRECTORY")
}

def run_command(command: str, cwd: str = None):
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    
def directory_validation(cwd:str) -> bool:
    
    custom_message = None
    
    try:
        os.chdir(cwd)
        return True
    
    except FileNotFoundError as e:
        custom_message = f"FileNotFoundError {e}"

    except Exception as e:
        custom_message = f"Exception {e}"

    if custom_message:
        print(custom_message)
    
    return False

def install_updates(cwd: str = None) -> bool:
    """Checks for new commits and dependancies in the remote repo by checking the status of the branch after fetching any new commits from the repo.
    If there are updates available, it will run the 'git pull' command before checking for any new dependancies in the 'requirements.txt' file.
    If there are any new dependacies, it will autmatically installs them"""

    if not directory_validation(cwd):
        print("Invalid directory")
        return False

    result = run_command(["git", "fetch"], cwd)
    
    if result.returncode != 0:
        print(result.stderr)
        return False

    result = run_command(["git", "status"], cwd)
    
    if result.returncode != 0:
        print(result.stderr)
        return False

    if "Your branch is behind" in result.stdout:
        
        result = run_command(["git", "pull"], cwd)

        if result.returncode != 0:
            print(result.stderr)
            return False
        
        print("New changes detected")
        check_and_install_new_dependencies()

    return True

def check_for_updates():

    sub_directories = directories_to_update()
    base_directory  = BASE_DIRECTORY_ENV["BASE_DIRECTORY"]
    
    for sub_directory in sub_directories:
        
        cwd = str(Path(base_directory) / sub_directory)
        
        if not install_updates(cwd):
            continue

if __name__ == "__main__":
    check_for_updates()