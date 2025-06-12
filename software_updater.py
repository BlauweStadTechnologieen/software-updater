import os
from error_handler import global_error_handler
from send_message import send_message
import zipfile
import requests
from requests.exceptions import HTTPError
from install_new_dependencies import update_requirements
from create_env_bundle import create_env_files


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

def get_latest_tag(repo_name:str, organization_name:str, organization_token:str) -> dict:
    
    print(f"Fetching latest tag for {repo_name}...")

    try:

        url = f"https://api.github.com/repos/{organization_name}/{repo_name}/releases/latest"
    
        headers = {

            "User-Agent": "Updater/1.0",
            "Authorization": f"token {organization_token}",

        }

        response = requests.get(url, headers=headers)

        response.raise_for_status()

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

def install_updates(repo_name:str, target_dir:str, organization_owner:str, organization_token:str) -> bool:
    """
    Downloads and extracts the GitHub repo as a ZIP into the target_dir (flattened).
    
    """

    release_tag = get_latest_tag(repo_name, organization_owner, organization_token)
    zip_url     = f"https://github.com/{organization_owner}/{repo_name}/archive/refs/tags/{release_tag}.zip"
    zip_path    = os.path.join(target_dir, "temp_repo.zip")

    if not version_check(repo_name, target_dir, organization_owner):
        
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
    
    except Exception as e:
        
        global_error_handler("Installation failure", f"Failed to update {repo_name}: {e}")
        
        return False
    
def version_check(repo_name:str, cwd:str, organization_owner:str) -> bool:
    """
    Checks if the latest version of the repository is already installed.
    Args:
        repo_name (str): The name of the repository to check.
    Returns:
        bool: True if the latest version is installed, False otherwise.
    """    
    try:
    
        api_url = f"https://api.github.com/repos/{organization_owner}/{repo_name}/releases"

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
    
import os

def validate_base_directory() -> str | None:
    
    while True:

        try:

            root_directory = input("Please enter the base directory: ").strip()

            if not root_directory:
                raise ValueError("No directory path was provided.")
            
            if not os.path.exists(root_directory):
                raise FileNotFoundError(f"The path '{root_directory}' does not exist.")
            
            if not os.path.isdir(root_directory):
                raise NotADirectoryError(f"The path '{root_directory}' is not a directory.")
            
            return root_directory

        except (ValueError, FileNotFoundError, NotADirectoryError) as e:

            global_error_handler("Invalid base directory", str(e))

def validate_personal_access_token() -> str | None:

    while True:
    
        try:
        
            personal_access_token = input("Please enter your Gethub Personal Access Token (PAT).....").strip()
            
            if not personal_access_token:

                raise KeyError("No Personal Access Token was entered, this is a mandatory entry....")
            
            if len(personal_access_token) < 40:

                raise ValueError("Invalid Personal Access Token length")
            
            headers = {"Authorization": f"token {personal_access_token}"}
            response = requests.get("https://api.github.com/user", headers=headers)
            
            response.raise_for_status()
            
            return personal_access_token
        
        except (HTTPError, KeyError, ValueError) as e:

            global_error_handler("Invalid Personal Access Token",f"{e}")

def github_owner_validation(personal_access_token: str) -> str | None:
    
    from requests.exceptions import HTTPError

    try:
        # First, get the authenticated user
        auth_response = requests.get(

            "https://api.github.com/user",

            headers={

                "Authorization": f"token {personal_access_token}",
                "Accept": "application/vnd.github.v3+json"

            }
        )

        auth_response.raise_for_status()
        
        authenticated_user = auth_response.json()["login"]

    except HTTPError as e:

        raise RuntimeError("Failed to authenticate with the provided GitHub token") from e

    while True:
        
        try:

            organization_owner = input("Enter the GitHub owner (username or org): ").strip()

            if not organization_owner:
                raise KeyError("No GitHub owner was specified")

            # Check existence of org first, then fallback to user
            url = f"https://api.github.com/orgs/{organization_owner}"

            headers = {

                "Authorization": f"token {personal_access_token}",
                "Accept": "application/vnd.github.v3+json"

            }
            
            response = requests.get(url, headers=headers)

            if response.status_code == 404:

                url = f"https://api.github.com/users/{organization_owner}"

                response = requests.get(url, headers=headers)

            response.raise_for_status()

            if organization_owner != authenticated_user:

                raise PermissionError(f"The GitHub owner '{organization_owner}' does not match the authenticated user '{authenticated_user}'.")

            print(f"Owner '{organization_owner}' validated and matches the authenticated user.")
            
            return organization_owner

        except PermissionError as e:

            print(f"Permission Error: {e}")

        except HTTPError as e:

            status = e.response.status_code

            if status == 401:

                print("Unauthorized: Token is invalid or expired.")

            elif status == 404:

                print("Not Found: No such GitHub user/org.")

            else:

                print(f"HTTP Error: {e}")

        except KeyError as e:

            print(f"input Error: {e}")

def validate_mql5_directory() -> str | None:

    while True:
    
        try:

            mql5_root_directory = input("Please enter your MQL5 base directory: ").strip()

            if not mql5_root_directory:
                raise ValueError("No directory path was provided.")
            
            if not os.path.exists(mql5_root_directory):
                raise FileNotFoundError(f"The path '{mql5_root_directory}' does not exist.")
            
            if not os.path.isdir(mql5_root_directory):
                raise NotADirectoryError(f"The path '{mql5_root_directory}' is not a directory.")
            
            return mql5_root_directory

        except (ValueError, FileNotFoundError, NotADirectoryError) as e:

            global_error_handler("Invalid MQL5 directory", str(e))

def check_for_updates():
    
    """
    Loops through all of the specified directories by constructing each directory, checks for their validity, checks for any changes before installing them.
    This will check the validity of the base directory first. If this fails, the script will exit early.
    Notes:
    -
    Any exceptions or error will be handles and processed by the `error_handler` module.
    """

    root_directory          = validate_base_directory()
    personal_access_token   = validate_personal_access_token()
    organization_owner      = github_owner_validation(personal_access_token)
    mql5_root_directory     = validate_mql5_directory()
                            
    REPO_MAPPING = {

        "software-updater"          : "software-updater",
        "git-commit"                : "github-push-script",
        "vm-status-monitor"         : "azure-vm-monitor",
        "create-virtual-environment": "create-virtual-environment",
    }

    
    for package in REPO_MAPPING.keys():
        
        try:
        
            package_directory = os.path.join(root_directory, package)

            if os.path.exists(package_directory):
                
                continue
            
            os.makedirs(package_directory, exist_ok=True)

            if not create_env_files(package_directory, root_directory, personal_access_token, organization_owner, mql5_root_directory):

                return
            
            if not update_requirements(package_directory):

                return

        except OSError as e:
            
            global_error_handler("Directory Creation OS Error", f"Failed to create directory for {package}: {e}")
            
        except Exception as e:

            global_error_handler("Directory Creation Error", f"Failed to create directory for {package}: {e}")
    
    updated_software_packages = []

    BASE_DIRECTORY = root_directory
            
    try:
        
        for software_package in os.listdir(BASE_DIRECTORY):
            
            cwd = os.path.join(BASE_DIRECTORY, software_package)
            
            if software_package not in REPO_MAPPING.keys():

                print(f"Skipping {software_package} as it is not in the mapping.")
                
                continue

            remote_git_repo = REPO_MAPPING[software_package]
            
            if not install_updates(remote_git_repo, cwd, organization_owner, personal_access_token):
                
                continue
                                    
            updated_software_packages.append(software_package)
        
        if updated_software_packages:

            print("Updated Packages present....")
                        
            send_message(updated_software_packages)

    except OSError as e:

        global_error_handler("OS Error","There was an error when running a subprocess")
    
    except Exception as e:
                    
        global_error_handler("Error in checking for updates", f"Unfortunately, there was an error in checking for updates. Please find the following error message {e}")
        
if __name__ == "__main__":
    check_for_updates()