import subprocess
import hashlib
import os
from directories_to_update import directories_to_update
from pathlib import Path
from install_new_dependancies import check_and_install_new_dependancies
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
        custom_message = f"Whoops {e}"

    except Exception as e:
        custom_message = f"Whoops {e}"

    if custom_message:
        print(custom_message)
    
    return False

def install_updates(cwd: str = None) -> bool:
    """Checks for remote commits and updates the local repository if needed."""

    if not directory_validation(cwd):
        print("Invalid directory")
        return False

    def run_git_command(command: list, error_message: str):
        result = run_command(command, cwd)
        if result.returncode != 0:
            print(f"{error_message}: {result.stderr if result.stderr else result.returncode}")
            return False
        return result

    if not (result := run_git_command(["git", "fetch"], "Git Fetch Error")):
        return False

    if not (result := run_git_command(["git", "status"], "Git Status Error")):
        return False

    # Pull if needed
    if "Your branch is behind" in result.stdout:
        if not (pull_result := run_git_command(["git", "pull"], "Git Pull Error")):
            return False
        print("Pull complete")
        check_and_install_new_dependancies()

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
    
        

   

