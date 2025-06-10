import os
from dotenv import load_dotenv
from error_handler import global_error_handler
import send_message as message
import zipfile
import requests
from requests.exceptions import HTTPError
from get_extract_to_directory import get_extract_to_directory
from install_new_dependencies import update_requirements
from create_env_bundle import create_env_files
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

    except requests.HTTPError as e:

        global_error_handler("HTTP API Error",f"There was an error in retrieving the data from our servers - {e}")

        return None
    
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

    url = url = f"https://api.github.com/repos/{github_owner}/{repo_name}/releases/latest"
    
    headers = {'User-Agent': 'Updater/1.0'}

    github_api_token = os.getenv("GITHUB_TOKEN")

    if github_api_token:
    
        headers["Authorization"] = f"Bearer {github_api_token}"

    #print(headers)
    
    try:

        response = requests.get(url, headers=headers)

        response.raise_for_status()

        #print(f"GitHub API Status Code: {response.status_code}")
        #print("Response JSON:", response.text)

        get_latest_release_tag = response.json()
        latest_release_tag = get_latest_release_tag.get("tag_name") 
        
        if not latest_release_tag:
            
            raise ValueError(f"No tags found for {repo_name}, please ensure that you have created a tag for the latest release.")
        
        return latest_release_tag 
    
    except HTTPError as e:

        global_error_handler("GitHub API HTTP Error", f"HTTP error occurred while fetching tags for {repo_name}: {e}")
        
        return None
    
    except requests.RequestException as e:
        
        global_error_handler("GitHub API Request Error", f"Failed to fetch tags for {repo_name}: {e}")

        return None
    
    except Exception as e:
        
        global_error_handler("Tag Retrieval Error", f"An error occurred while retrieving the latest tag for {repo_name}: {e}")
        
        return None

def install_updates(repo_name, target_dir) -> bool:
    """
    Downloads and extracts the GitHub repo as a ZIP into the target_dir (flattened).
    """
    release_tag = get_latest_tag(repo_name)
    zip_url     = f"https://github.com/{github_owner}/{repo_name}/archive/refs/tags/{release_tag}.zip"
    zip_path    = os.path.join(target_dir, "temp_repo.zip")

    if not version_check(repo_name, target_dir):
        
        return False
    
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
    except HTTPError as e:
        
        global_error_handler("HTTP Error", f"A HTTP error occurred while downloading {repo_name}: {e}")
        
        return False
        return False
    
    except Exception as e:
        
        global_error_handler("Installation failure", f"Failed to update {repo_name}: {e}")
        
        return False
    
def version_check(repo_name:str, cwd:str) -> bool:
    """
    Checks if the latest version of the repository is already installed.
    Args:
        repo_name (str): The name of the repository to check.
    Returns:
        bool: True if the latest version is installed, False otherwise.
    """
    
    try:
    
        api_url = f"https://api.github.com/repos/{github_owner}/{repo_name}/releases"

        release_file = "current_release.txt"

        release_file_dir = os.path.join(cwd, release_file)
        
        response = requests.get(api_url)

        if response.status_code == 200:
            
            release_data = response.json()

            if not release_data:
                
                global_error_handler("No releases found", "This repository has no releases available.")

                return False

            if os.path.exists(release_file_dir):
                
                with open(release_file_dir, "r") as f:

                    stored_release = f.read().strip()

            else:

                stored_release = None

            latest_release = release_data[0]["tag_name"]

            #print(stored_release, latest_release)

            if stored_release != latest_release:

                with open(release_file_dir, "w") as f:

                    f.write(latest_release)

                    return True
                
            else:
                
                print("No new release found, current version is up to date.")
                
                return False

        else:

            raise Exception(f"Failed to fetch latest release data: {response.status_code} - {response.text}")
                    
    except requests.RequestException as e:
        
        global_error_handler("Version Check Error", f"An error occurred while checking the version of {repo_name}: {e}")

        return False

    except Exception as e:
        
        global_error_handler("Version Check Error", f"An unexpected error occurred while checking the version of {repo_name}: {e}")

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

    
    for package in REPO_MAPPING.keys():
        
        try:
        
            extract_to = os.path.join(BASE_DIRECTORY, package)

            if os.path.exists(extract_to):
                
                continue
            
            os.makedirs(extract_to, exist_ok=True)

            if not create_env_files(extract_to):

                continue

        except OSError as e:
            
            global_error_handler("Directory Creation Error", f"Failed to create directory for {package}: {e}")
            
        except Exception as e:

            global_error_handler("Directory Creation Error", f"Failed to create directory for {package}: {e}")
    
    updated_software_packages = []
            
    try:
        
        for software_package in os.listdir(BASE_DIRECTORY):
            
            cwd = os.path.join(BASE_DIRECTORY, software_package)
            
            if software_package not in REPO_MAPPING:

                print(f"Skipping {software_package} as it is not in the mapping.")
                
                continue

            remote_git_repo = REPO_MAPPING[software_package]
            
            if not install_updates(remote_git_repo, cwd):
                
                continue
            
            venv_dir = os.path.join(cwd, ".venv")

            if os.path.isdir(venv_dir):
            
                if not update_requirements(cwd):

                    break
                
            else:

                print(f"Virtual environment not found for {software_package}. Skipping the installation of dependancies. You will need to create a .venv and install the requirements manually.")
            
            updated_software_packages.append(software_package)
        
        if updated_software_packages:

            print("Updated Packages")
                        
            message.send_message(updated_software_packages)

    except OSError as e:

        global_error_handler("OS Error","There was an error when running a subprocess")
    
    except Exception as e:
                    
        global_error_handler("Error in checking for updates", f"Unfortunately, there was an error in checking for updates. Please find the following error message {e}")
        
if __name__ == "__main__":
    check_for_updates()