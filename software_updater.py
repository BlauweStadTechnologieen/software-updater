import subprocess
import os
from install_new_dependencies import check_and_install_new_dependencies
from dotenv import load_dotenv
from pathlib import Path
from error_handler import global_error_handler
import send_message as message

load_dotenv()

BASE_DIRECTORY_ENV = {
    "BASE_DIRECTORY" : os.getenv("BASE_DIRECTORY")
}

def run_command(command: str, cwd: str = None):
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    
def directory_validation(cwd:str) -> bool:
        
    error_message_type = "Directory Validation Error"
    
    try:
        os.chdir(cwd)
        print("You should not see this message")
        directory_contents = os.listdir(cwd)
        
        if ".git" in directory_contents:
            return True
        else:
            print(f"The {cwd} is unfortunatley not a git repo")
            return global_error_handler(f"{error_message_type}",f"This is not a local git repository. Please navigate to {cwd} and run 'git init' to initialise the folder.")
    
    except FileNotFoundError as e:
        return global_error_handler(f"{error_message_type} FileNotFound Error", f"FileNotFoundError {e} for Directory {cwd}")

    except Exception as e:
        return global_error_handler(f"{error_message_type} Exception Error", f"Exception{e}")

def install_updates(cwd: str = None) -> bool:
    """Checks for new commits and dependancies in the remote repo by checking the status of the branch after fetching any new commits from the repo.
    If there are updates available, it will run the 'git pull' command before checking for any new dependancies in the 'requirements.txt' file.
    If there are any new dependacies, it will autmatically installs them"""
    
    error_message_type = "Update Installation Error"
    
    if not directory_validation(cwd):
        return global_error_handler(f"{error_message_type}", f"The directory {cwd} is not valid. Please double-check the validity of the directory and try again. We apologise for the inconvenience caused. No, we are not Indian!")
    
    commands = {
        "fetch"  : ["git", "fetch"],
        "status" : ["git", "status"]
        # Note: "pull" is not included here, as it is conditionally executed based on "status" output.
    }
    
    for cmd_name, cmd_args in commands.items():
        result = run_command(cmd_args, cwd)
        if result.returncode != 0:
            return global_error_handler(f"{error_message_type}", f"Git {cmd_name.capitalize()} Error # {result.returncode}.")
        
        if cmd_name == "status" and "Your branch is behind" in result.stdout:

            result = run_command(["git","pull"], cwd)
            if result.returncode != 0:
                return global_error_handler(f"{error_message_type}", f"Git Pull Error {result.returncode} {result.stdout}")

            print("New changes detected")
            check_and_install_new_dependencies()

    return True

def check_for_updates():

    try:
        
        base_directory              = BASE_DIRECTORY_ENV["BASE_DIRECTORY"]
        
        if not base_directory:
            raise KeyError("BASE_DIRECTORY key not found in BASE_DIRECTORY_ENV.")

        if not os.path.isdir(base_directory):
            raise FileNotFoundError(f"Base directory '{base_directory}' does not exist") 
        
        updated_software_packages   = []
    
        for software_package in os.listdir(base_directory):
                    
            cwd = os.path.join(base_directory, software_package)
            
            if not install_updates(cwd):
                continue

            updated_software_packages.append(software_package)
        
        message.send_message(updated_software_packages)

    except KeyError as e:

        return global_error_handler("Key Error", f"{e}")
    
    except FileNotFoundError as e:

        return global_error_handler("File Not Found Error", f"{e}")
    
    except Exception as e:

        return global_error_handler("Error","f{e}")

if __name__ == "__main__":
    check_for_updates()