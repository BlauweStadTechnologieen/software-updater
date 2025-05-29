import os
from dotenv import load_dotenv
from error_handler import global_error_handler
import send_message as message
import zipfile
import io
import requests
from get_extract_to_directory import get_extract_to_directory
from install_new_dependencies import update_requirements
load_dotenv()

github_owner    = os.getenv("GITHUB_USERNAME")    
BASE_DIRECTORY  = get_extract_to_directory()   

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

def extract_zip_flat(zip_path:str, target_dir:str):
    
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

def get_latest_tag(repo_name:str) -> dict:
    
    print(f"Fetching latest tag for {repo_name}...")

    url = f"https://api.github.com/repos/{github_owner}/{repo_name}/tags"
    
    headers = {'User-Agent': 'Updater/1.0'}

    github_api_token = os.getenv("GITHUB_TOKEN")

    if github_api_token:
    
        headers["Authorisation"] = f"Bearer {os.getenv('GITHUB_TOKEN')}"
    
    response = requests.get(url, headers=headers)
    
    tags = response.json()

    try:
    
        if not tags:
            
            raise Exception(f"No tags found for {repo_name}, please ensure that you have created a tag for the latest release.")
        
        return tags[0]['name'] 
    
    except requests.RequestException as e:
        
        global_error_handler("GitHub API Request Error", f"Failed to fetch tags for {repo_name}: {e}")

        return None
    
    except Exception as e:
        
        global_error_handler("Tag Retrieval Error", f"An error occurred while retrieving the latest tag for {repo_name}: {e}")
        
        return None

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
    
    if BASE_DIRECTORY is None: 
                
        return
    
    REPO_MAPPING = {

        "software-updater"          : "software-updater",
        "git-commit"                : "github-push-script",
        "vm-status-monitor"         : "azure-vm-monitor",
        "create-virtual-environment": "create-virtual-environment",
    }

    try:
    
        for package in REPO_MAPPING.keys():
            
            extract_to = os.path.join(BASE_DIRECTORY, package)
            
            os.makedirs(extract_to, exist_ok=True)

    except Exception as e:

        global_error_handler("Directory Creation Error", f"Failed to create directory for {package}: {e}")

        return
    
    updated_software_packages = []
            
    try:
        
        for software_package in os.listdir(BASE_DIRECTORY):
            
            cwd = os.path.join(BASE_DIRECTORY, software_package)
            
            if software_package not in REPO_MAPPING:

                print(f"Skipping {software_package} as it is not in the mapping.")
                
                continue

            github_repo = REPO_MAPPING[software_package]
            
            if not install_updates(github_repo, cwd):
                
                continue
            
            venv_dir = os.path.join(cwd, ".venv")

            if os.path.exists(venv_dir):
            
                if not update_requirements(cwd):

                    break
                
            else:

                print(f"Virtual environment not found for {software_package}. Skipping the installation of dependancies. You will need to create a .venv and install the requirements manually.")
            
            updated_software_packages.append(software_package)
        
        if updated_software_packages:
                        
            message.send_message(updated_software_packages)

    except Exception as e:
                    
        global_error_handler("Error in checking for updates", f"Unfortunately, there was an error in checking for updates. Please find the following error message {e}")
        
        return

if __name__ == "__main__":
    check_for_updates()