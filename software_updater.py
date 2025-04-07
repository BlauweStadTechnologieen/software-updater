import subprocess
import os
from install_new_dependencies import check_and_install_new_dependencies
from dotenv import load_dotenv
from error_handler import global_error_handler
import send_message as message

load_dotenv()

BASE_DIRECTORY_ENV = {
    "BASE_DIRECTORY" : os.getenv("BASE_DIRECTORY")
}

base_directory = BASE_DIRECTORY_ENV["BASE_DIRECTORY"]

def run_command(command: str, cwd: str = None):
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True)

def base_directory_validation(base_directory:str) -> bool:
    """
    Checks the validity of the base directory. This is retrieved from the `.env` file.
    Args:
        base_directory(str): Denoted the path of the base directory
    Returns:
        base_directory(str): Returns the path of the base directory
    Exceptions:
        KeyError: A KeyError is raised when no base directory is specified
        FileNotFoundError: Raised whe a base directory is specified, how this is incorrect. It will prompt you to double check this. 
    """
    try:
    
        if not base_directory:
            raise KeyError(f"Please specify a base directory in the '.env' file.")

        if not os.path.isdir(base_directory):
            raise FileNotFoundError(f"Base directory '{base_directory}' does not exist") 
        
    except KeyError as e:
        
        global_error_handler(f"Base Directory Key Error",f"The key for the base directory .env is missing. {e}")
        
        return False

    except FileNotFoundError as e:
        
        global_error_handler("Invalid base directory", f"Unfortunately we unable to find the {base_directory} on the system. - {e}")
        
        return False
    
    return True

def directory_validation(cwd:str) -> bool:
        
    """
    Checks cor the validity of the full directory. 
    Args:
        cwd(str):Denotes the current working directory.
    Returns:
        bool: True if the directory is valid, else returns False.
    Exceptions:
        FileNotFoundError: Raised when the file is not found and therefire the direcvory is invalid.
        Exception: Raised when any other error is thrown.
    """
    
    error_message_type = "Directory Validation Error"
    
    try:
        
        os.chdir(cwd)
        
        directory_contents = os.listdir(cwd)
        
        if ".git" in directory_contents:
                        
            return True
        
        global_error_handler(f"{error_message_type}",f"This is not a local git repository. Please navigate to {cwd} and run 'git init' to initialise the folder.")
            
    except FileNotFoundError as e:
        
        global_error_handler(f"{error_message_type} FileNotFound Error", f"FileNotFoundError {e} for Directory {cwd}")
        
    except Exception as e:

        global_error_handler(f"{error_message_type} Exception Error", f"Exception - {e}")
        
    return False

def install_updates(cwd: str = None) -> bool:
    """Installs any new package updates by checking for differences between the local machine and the remote repository. If there are any new commits since the previous update, it will install the update.
    Args:
        cwd(str, optional): Denotes the current working directory.
    Returns:
        bool: True if there are no errors and that updates have been successfully installed, else returns False.
    Notes:
    -
    The script will now also install any new dependances from the `requirements.txt` file if any new dependancies have been detected. If they have, the script will install these as well.

    """
    
    error_message_type = "Update Installation Error"
    
    if not directory_validation(cwd):
        return False
    
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
    """
    Loops through all of the specified directories by constructing each directory, checks for their validity, checks for any changes before installing them.
    This will check the validity of the base directory first. If this fails, the script will exit early.
    Notes:
    -
    Any exceptions or error will be handles and processed by the `error_handler` module.
    """
    
    updated_software_packages = []

    if not base_directory_validation(base_directory):
                
        return
        
    else:
    
        try:
            
            for software_package in os.listdir(base_directory):
                
                cwd = os.path.join(base_directory, software_package)
                                
                if not install_updates(cwd):
                                        
                    continue 
                
                updated_software_packages.append(software_package)
            
            if updated_software_packages:

                message.send_message(updated_software_packages)

        except Exception as e:
                        
            global_error_handler("Error in checking for updates", f"Unfortunately, there was an error in checking for updates. Please find the following error message {e}")
            
            return

if __name__ == "__main__":
    check_for_updates()