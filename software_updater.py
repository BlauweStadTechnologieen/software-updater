import os
from install_new_dependencies import check_and_install_new_dependencies
from dotenv import load_dotenv
from error_handler import global_error_handler
import send_message as message
import zipfile
import io
import requests

load_dotenv()

BASE_DIRECTORY_ENV = {
    "BASE_DIRECTORY" : os.getenv("BASE_DIRECTORY")
}

base_directory = BASE_DIRECTORY_ENV["BASE_DIRECTORY"]

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

def get_latest_release_zip_url(repo:str) -> str:
    """
    Retrieves the latest release zip URL from the GitHub API.
    Args:
        repo(str): Denotes the name of the repository.
    Returns:
        str: The URL of the latest release zip file.
    """
    
    api_url = f"https://api.github.com/repos/BlauweStadTechnologieen/{repo}/releases/latest"

    try:
        
        response = requests.get(api_url)
        response.raise_for_status()
        release_data = response.json()
        return release_data["zipball_url"]
    
    except requests.RequestException as e:
        
        global_error_handler("GitHub API Error", f"Failed to fetch the latest release zip URL: {e}")
        
        return None

def download_and_extract_zip(repo:str, extract_to:str) -> bool:
    """
    Downloads the latest release zip file from the specified GitHub repository and extracts its contents to the given directory.
    Args:
        repo (str): The GitHub repository in the format 'owner/repo'.
        extract_to (str): The directory to extract the contents to.
    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    zip_url = get_latest_release_zip_url(repo)
    
    if not zip_url:
                
        custom_subject = f"Failed to get the latest release zip URL for {repo}"
        custom_message = f"Failed to get the latest release zip URL for {repo}. Please check the repository name and try again."
        global_error_handler(custom_subject, custom_message)
        
        return False    
    
    try:
        
        response = requests.get(zip_url)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            
            if os.path.exists(extract_to):
                
                for filename in os.listdir(extract_to):
                    
                    file_path = os.path.join(extract_to, filename)
                    
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                       
                       os.unlink(file_path)
                    
                    elif os.path.isdir(file_path):
                        
                        import shutil
                        
                        shutil.rmtree(file_path)

            zip_ref.extractall(extract_to)

        return True
    
    except PermissionError as e:
        
        global_error_handler("Permission Error", f"Permission denied: {e}")
        
        return False

    except FileNotFoundError as e:
        
        global_error_handler("File Not Found Error", f"File not found: {e}")
        
        return False
    
    except requests.RequestException as e:
        
        global_error_handler("Request Error", f"Request error: {e}")
        
        return False
    
    except zipfile.BadZipFile as e:
        
        global_error_handler("Bad Zip File Error", f"Bad zip file: {e}")
        
        return False    
    
    except Exception as e:
        
        global_error_handler("General Error", f"An error occurred: {e}")
        
        return False

def install_updates(repo:str, cwd: str = None) -> bool:
    """Installs any new package updates by checking for differences between the local machine and the remote repository. If there are any new commits since the previous update, it will install the update.
    Args:
        cwd(str, optional): Denotes the current working directory.
    Returns:
        bool: True if there are no errors and that updates have been successfully installed, else returns False.
    Notes:
    -
    The script will now also install any new dependances from the `requirements.txt` file if any new dependancies have been detected. If they have, the script will install these as well.

    """
    
    download_and_extract_zip(repo, cwd)

    check_and_install_new_dependencies() 
    

def check_for_updates():
    """
    Loops through all of the specified directories by constructing each directory, checks for their validity, checks for any changes before installing them.
    This will check the validity of the base directory first. If this fails, the script will exit early.
    Notes:
    -
    Any exceptions or error will be handles and processed by the `error_handler` module.
    """
    
    REPO_MAPPING = {

        "software-updater"      : "software-updater",
        "git-commit"            : "github-push-script",
        "vm-status-monitor"     : "azure-vm-monitor",
    }
    
    updated_software_packages = []

    if not base_directory_validation(base_directory):
                
        return
            
    try:
        
        for software_package in os.listdir(base_directory):
            
            cwd = os.path.join(base_directory, software_package)
            
            if software_package not in REPO_MAPPING:

                print(f"Skipping {software_package} as it is not in the mapping.")
                
                continue

            github_repo = REPO_MAPPING[software_package]
            
            if not install_updates(github_repo, cwd):
                                    
                continue 
            
            updated_software_packages.append(software_package)
        
        if updated_software_packages:

            message.send_message(updated_software_packages)

    except Exception as e:
                    
        global_error_handler("Error in checking for updates", f"Unfortunately, there was an error in checking for updates. Please find the following error message {e}")
        
        return

if __name__ == "__main__":
    check_for_updates()