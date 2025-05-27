import os
from dotenv import load_dotenv
from error_handler import global_error_handler
import send_message as message
import zipfile
import io
import requests

load_dotenv()

base_directory  = os.getenv("BASE_DIRECTORY")
github_owner    = os.getenv("GITHUB_USERNAME")

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
        
    except KeyError as key_error:
        
        global_error_handler("Missing base directory in your .env file",f"The key for the base directory within your .env file is missing. {key_error}")
        
        return False

    except FileNotFoundError as e:
        
        global_error_handler("The specified base directory in your .env file is invalid", f"Unfortunately we unable to find the {base_directory} on the system. - {e}")
        
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
    
    api_url = f"https://api.github.com/repos/{github_owner}/{repo}/releases/latest"

    try:
        
        response = requests.get(api_url)
        response.raise_for_status()
        release_data = response.json()
        return release_data["zipball_url"]
    
    except requests.RequestException as e:
        
        global_error_handler("Latest ZIP URL retrieval error", f"Failed to fetch the latest release ZIP URL for: {e}")
        
        return None

def extract_zip_flat(zip_path, target_dir):
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        
        members = zip_ref.namelist()
        
        # Detect common prefix (like repo-main/)
        common_prefix = os.path.commonprefix(members)
        
        if not common_prefix.endswith("/"):
            
            common_prefix = os.path.dirname(common_prefix) + "/"

        for member in members:
            
            if member.endswith("/"):
                
                continue
            
            member_path = member[len(common_prefix):]
            target_path = os.path.join(target_dir, member_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            with zip_ref.open(member) as source, open(target_path, "wb") as target:
                
                target.write(source.read())

def get_latest_tag(repo_name):
    
    print(f"Fetching latest tag for {repo_name}...")

    url = f"https://api.github.com/repos/{github_owner}/{repo_name}/tags"
    
    headers = {'User-Agent': 'Updater/1.0'}

    github_api_token = os.getenv("GITHUB_TOKEN")

    if github_api_token:
    
        headers["Authorisation"] = f"Bearer {os.getenv('GITHUB_TOKEN')}"
    
    response = requests.get(url, headers=headers)
    
    tags = response.json()

    if not tags:
        
        raise Exception(f"No tags found for {repo_name}")
    
    return tags[0]['name'] 

def install_updates(repo_name, target_dir):
    """
    Downloads and extracts the GitHub repo as a ZIP into the target_dir (flattened).
    """
    release_tag = get_latest_tag(repo_name)

    zip_url = f"https://github.com/{github_owner}/{repo_name}/archive/refs/tags/{release_tag}.zip"

    zip_path = os.path.join(target_dir, "temp_repo.zip")

    try:
        response = requests.get(zip_url)
        response.raise_for_status()

        with open(zip_path, "wb") as f:
            f.write(response.content)

        # Extract directly into the target directory
        extract_zip_flat(zip_path, target_dir)

        # Optionally: clean up
        os.remove(zip_path)
        
        return True
    
    except requests.RequestException as e:
        
        print(f"Request to {zip_url} failed with status {response.status_code}")
        
        global_error_handler("Request Exception Error", f"Failed to download and install the latest release of {repo_name}: {e}")
        
        return False
    
    except requests.exceptions.HTTPError as e:
        
        global_error_handler("HTTP Error", f"A HTTP error occurred while downloading {repo_name}: {e}")
        
        return False
    
    except Exception as e:
        
        global_error_handler("Installation failure", f"Failed to update {repo_name}: {e}")
        
        return False

def check_for_updates():
    """
    Loops through all of the specified directories by constructing each directory, checks for their validity, checks for any changes before installing them.
    This will check the validity of the base directory first. If this fails, the script will exit early.
    Notes:
    -
    Any exceptions or error will be handles and processed by the `error_handler` module.
    """
    
    REPO_MAPPING = {

        "software-updater"          : "software-updater",
        "git-commit"                : "github-push-script",
        "vm-status-monitor"         : "azure-vm-monitor",
        "create-virtual-environment": "create-virtual-environment",
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