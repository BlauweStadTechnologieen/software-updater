import subprocess
import os
from install_new_dependencies import check_and_install_new_dependencies
from dotenv import load_dotenv
from pathlib import Path
from error_handler import global_error_handler, generate_support_ticket
import send_message as message

load_dotenv()

BASE_DIRECTORY_ENV = {
    "BASE_DIRECTORY" : os.getenv("BASE_DIRECTORY")
}

base_directory = BASE_DIRECTORY_ENV["BASE_DIRECTORY"]

def run_command(command: str, cwd: str = None):
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True)

def base_directory_validation() -> bool:
    
    try:
    
        if not base_directory:
            raise KeyError(f"The specified base directory of {base_directory} key is missing")

        if not os.path.isdir(base_directory):
            raise FileNotFoundError(f"Base directory '{base_directory}' does not exist") 
        
    except KeyError as e:
        
        global_error_handler(f"Base Directory Key Error","The key for the base directory env is either incorrect or missing. Please check for validation {e}")
        
        return False

    except FileNotFoundError as e:
        
        global_error_handler("Base Directory Existence", f"Unfortunately we unable to find the {base_directory} on the system {e}")
        
        return False

    except Exception as e:
        
        global_error_handler("Base Directory General Exception", f"{e}")
        
        return False
    
    return True

def directory_validation(cwd:str) -> bool:
        
    error_message_type = "Directory Validation Error"
    
    try:

        os.chdir(cwd)
        
        directory_contents = os.listdir(cwd)
        
        if ".git" in directory_contents:
            
            return True
        
        else:
           
            global_error_handler(f"{error_message_type}",f"This is not a local git repository. Please navigate to {cwd} and run 'git init' to initialise the folder.")
            
            return False

    except FileNotFoundError as e:
        
        global_error_handler(f"{error_message_type} FileNotFound Error", f"FileNotFoundError {e} for Directory {cwd}")
        
        return False

    except Exception as e:
        
        global_error_handler(f"{error_message_type} Exception Error", f"Exception{e}")
        
        return False

def install_updates(cwd: str = None) -> bool:
    """Checks for new commits and dependancies in the remote repo by checking the status of the branch after fetching any new commits from the repo.
    If there are updates available, it will run the 'git pull' command before checking for any new dependancies in the 'requirements.txt' file.
    If there are any new dependacies, it will autmatically installs them"""
    
    error_message_type = "Update Installation Error"
        
    commands = {
        "fetch"  : ["git", "fetch"],
        "status" : ["git", "status"]
        # Note: "pull" is not included here, as it is conditionally executed based on "status" output.
    }
    
    for cmd_name, cmd_args in commands.items():
        
        result = run_command(cmd_args, cwd)
        
        if result.returncode != 0:
            
            global_error_handler(f"{error_message_type}", f"Git {cmd_name.capitalize()} Error # {result.returncode}.")
            
            return False

        if cmd_name == "status" and "Your branch is behind" in result.stdout:

            result = run_command(["git","pull"], cwd)
            
            if result.returncode != 0:
                
                global_error_handler(f"{error_message_type}", f"Git Pull Error {result.returncode}-{result.stdout}")
                
                return False

            print("New changes detected")
            check_and_install_new_dependencies()

    return True

def check_for_updates():

    updated_software_packages = []

    if base_directory_validation():
        
        try:
            
            for software_package in os.listdir(base_directory):
                
                cwd = os.path.join(base_directory, software_package)
                
                if not install_updates(cwd):
                                        
                    continue 

                updated_software_packages.append(software_package)
            
            if updated_software_packages:

                message.send_message(updated_software_packages)

        except Exception as e:
            
            generate_support_ticket("Error in checking for updates", f"Unfortunately, there was an error in checking for updates. Please find the folloiwing error message {e}")
            
            return

if __name__ == "__main__":
    check_for_updates()