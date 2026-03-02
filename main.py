import os
from error_handler import global_error_handler
import zipfile
from install_new_dependencies import update_requirements
from create_env_bundle import create_env_files
import getpass
from urllib import request, error
import json
import logging

logger = logging.getLogger(__name__)

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
    
    global_error_handler("Fetching latest tag", f"Attempting to fetch the latest tag for {repo_name} from GitHub....", logging_level=logging.INFO)

    try:

        url = f"https://api.github.com/repos/{organization_name}/{repo_name}/releases/latest"
    
        headers = {

            "User-Agent"    : "Updater/1.0",
            "Authorization" : f"token {organization_token}",

        }

        req = request.Request(url, headers=headers, method="GET")

        with request.urlopen(req) as response:
            body                     = response.read().decode("utf-8")
            get_latest_release_tag   = json.loads(body)

            latest_release_tag = get_latest_release_tag.get("tag_name") 
        
            if not latest_release_tag:
                
                raise ValueError(f"No tags found for {repo_name}, please ensure that you have created a tag for the latest release.")
            
            return latest_release_tag 
    
    except error.HTTPError as e:
        
        global_error_handler("GitHub API HTTP Error", f"Failed to fetch tags for {repo_name}: {e.code} - {e.reason}", logging_level=logging.ERROR)

        return None
    
    except Exception as e:
        
        global_error_handler("Tag Retrieval Error", f"An error occurred while retrieving the latest tag for {repo_name}: {e}", logging_level=logging.ERROR)
        
        return None

def install_updates(repo_name:str, target_dir:str, organization_owner:str, organization_token:str) -> bool:
    """
    Downloads and extracts the GitHub repo as a ZIP into the target_dir (flattened).
    
    """

    release_tag = get_latest_tag(repo_name, organization_owner, organization_token)
    zip_url     = f"https://github.com/{organization_owner}/{repo_name}/archive/refs/tags/{release_tag}.zip"
    zip_path    = os.path.join(target_dir, "temp_repo.zip")

    if not version_check(repo_name, target_dir, organization_owner) or not release_tag:
        
        return False
    
    try:
        
        req = request.Request(zip_url, method="GET")

        with request.urlopen(req) as response:
        
            with open(zip_path, "wb") as f:
                f.write(response.read())

        # Extract directly into the target directory
        extract_zip_flat(zip_path, target_dir)

        # Optionally: clean up
        os.remove(zip_path)
        
        return True
    
    except error.HTTPError as e:
        
        global_error_handler("HTTP Error", f"A HTTP error occurred while downloading {repo_name}: {e.code} - {e.reason}", logging_level=logging.ERROR)
        
        return False
    
    except Exception as e:
        
        global_error_handler("Installation failure", f"Failed to update {repo_name}: {e}", logging_level=logging.ERROR)
        
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
        
        req = request.Request(api_url, method="GET")

        with request.urlopen(req) as response:
            
            body = response.read().decode("utf-8")
        
            if response.getcode() == 200:
                
                release_data = json.loads(body)

                if not release_data:
                    
                    global_error_handler("No releases found", "This repository has no releases available.", logging_level=logging.INFO)

                    return False

                if os.path.exists(release_file_dir):
                    
                    with open(release_file_dir, "r") as f:

                        stored_release = f.read().strip()

                else:

                    stored_release = None

                latest_release = release_data[0]["tag_name"]

                if stored_release != latest_release:

                    with open(release_file_dir, "w") as f:

                        f.write(latest_release)

                        return True
                    
                else:
                    
                    global_error_handler("No update required", f"The latest version of {repo_name} is already installed.", logging_level=logging.INFO)
                    
                    return False

            else:

                raise Exception(f"Failed to fetch latest release data: {response.getcode()} - {response.read().decode('utf-8')}")
                    
    except error.HTTPError as e:
        
        global_error_handler("Version Check Error", f"An error occurred while checking the version of {repo_name}: {e.code} - {e.reason}", logging_level=logging.ERROR)

        return False

    except Exception as e:
        
        global_error_handler("Version Check Error", f"An unexpected error occurred while checking the version of {repo_name}: {e}", logging_level=logging.ERROR)

        return False
    
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

            global_error_handler(type(e).__name__, str(e), logging_level=logging.WARNING)

def validate_personal_access_token() -> str | None:
    """
    Prompts the user for a GitHub Personal Access Token (PAT) and validates it.
    Loops until a valid token is provided or the user cancels.
    Returns the validated token string.
    """
    while True:
        try:
            # Prompt user securely
            personal_access_token = getpass.getpass(
                "Please enter your GitHub Personal Access Token (PAT): "
            ).strip()

            if not personal_access_token:
                raise ValueError("No Personal Access Token entered. This is required.")

            if len(personal_access_token) < 40:
                raise ValueError("Invalid Personal Access Token length.")

            headers = {
                "Authorization": f"token {personal_access_token}",
                "User-Agent": "Updater/1.0",
                "Accept": "application/vnd.github.v3+json",
            }

            req = request.Request(
                "https://api.github.com/user",
                headers=headers,
                method="GET"
            )

            # Validate token by making request
            with request.urlopen(req):
                global_error_handler(
                    "GitHub token validated",
                    "Personal Access Token validated successfully.",
                    logging_level=logging.INFO
                )
                return personal_access_token

        except error.HTTPError as e:
            if e.code == 401:
                global_error_handler(
                    "Invalid GitHub token",
                    "The provided token is invalid or expired.",
                    logging_level=logging.WARNING
                )
            else:
                global_error_handler(
                    "GitHub API error",
                    f"HTTP {e.code} during token validation: {e.reason}",
                    logging_level=logging.ERROR
                )

        except error.URLError as e:
            global_error_handler(
                "Network error",
                f"Could not connect to GitHub: {e.reason}",
                logging_level=logging.ERROR
            )

        except ValueError as e:
            global_error_handler(
                "Invalid input",
                str(e),
                logging_level=logging.WARNING
            )

def github_owner_validation(personal_access_token: str) -> str | None:
    
    headers = {
        "Authorization": f"token {personal_access_token}",
        "User-Agent": "Updater/1.0",
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        req = request.Request(
            "https://api.github.com/user",
            headers=headers,
            method="GET"
        )

        with request.urlopen(req) as response:
            body = response.read().decode("utf-8")
            authenticated_user = json.loads(body)["login"]

    except error.HTTPError as e:
        if e.code == 401:
            global_error_handler(
                "Unauthorized GitHub token",
                "The provided GitHub Personal Access Token is invalid or expired.",
                logging_level=logging.ERROR
            )
        else:
            global_error_handler(
                "GitHub API error",
                f"HTTP {e.code} while retrieving authenticated user: {e.reason}",
                logging_level=logging.ERROR
            )
        return None

    except error.URLError as e:
        global_error_handler(
            "Network error",
            f"Network error occurred while validating GitHub token: {e.reason}",
            logging_level=logging.ERROR
        )
        return None

    while True:

        try:

            organization_owner = input(
                "Enter the GitHub owner (username or org): "
            ).strip()

            if not organization_owner:
                raise ValueError("No GitHub owner was specified.")

            # ---- First try org endpoint ----
            org_url = f"https://api.github.com/orgs/{organization_owner}"
            req = request.Request(org_url, headers=headers, method="GET")

            try:
                with request.urlopen(req):
                    owner_exists = True
            except error.HTTPError as e:
                if e.code == 404:
                    owner_exists = False
                else:
                    raise

            # ---- If org not found, try user endpoint ----
            if not owner_exists:
                user_url = f"https://api.github.com/users/{organization_owner}"
                req = request.Request(user_url, headers=headers, method="GET")

                try:
                    with request.urlopen(req):
                        owner_exists = True
                except error.HTTPError as e:
                    if e.code == 404:
                        raise ValueError("No GitHub user or organization found.")
                    else:
                        raise

            # ---- Ensure it matches authenticated user ----
            if organization_owner != authenticated_user:
                raise PermissionError(
                    f"The GitHub owner '{organization_owner}' does not match "
                    f"the authenticated user '{authenticated_user}'."
                )

            global_error_handler(
                "GitHub owner validated",
                f"Owner '{organization_owner}' validated successfully.",
                logging_level=logging.INFO
            )

            return organization_owner

        except ValueError as e:
            global_error_handler(
                "GitHub owner validation error",
                str(e),
                logging_level=logging.WARNING
            )

        except PermissionError as e:
            global_error_handler(
                "GitHub owner validation error",
                str(e),
                logging_level=logging.WARNING
            )

        except error.HTTPError as e:
            global_error_handler(
                "GitHub API error",
                f"HTTP {e.code} during owner validation: {e.reason}",
                logging_level=logging.ERROR
            )

        except error.URLError as e:
            global_error_handler(
                "Network error",
                f"Network error during owner validation: {e.reason}",
                logging_level=logging.ERROR
            )

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

            global_error_handler(type(e).__name__, str(e), logging_level=logging.WARNING)

def check_for_updates():
    
    """
    Iterates through the specified directories, validates them, and installs updates only if changes are detected.
    The base directory is validated first; if invalid, the script exits early.
    All exceptions and errors are handled by the `error_handler` module.
    """
    
    root_directory          = validate_base_directory()
    personal_access_token   = validate_personal_access_token()
    organization_owner      = github_owner_validation(personal_access_token)
    mql5_root_directory     = validate_mql5_directory()
                            
    REPO_MAPPING = {

        "software-updater"          : "software-updater",
        "mql5-script-manager"       : "github-push-script",
        "vm-status-monitor"         : "azure-vm-monitor",

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

                global_error_handler("Package skipped", f"Skipped {software_package} as it is not in the repository mapping.", logging_level=logging.INFO)
                
                continue

            remote_git_repo = REPO_MAPPING[software_package]
            
            if not install_updates(remote_git_repo, cwd, organization_owner, personal_access_token):
                
                continue
                                    
            updated_software_packages.append(software_package)
        
        if updated_software_packages:

            global_error_handler("Updates installed", f"The following packages were updated: {', '.join(updated_software_packages)}", logging_level=logging.INFO)
                      
    except OSError as e:

        global_error_handler("OS Error","There was an error when running a subprocess")
    
    except Exception as e:
                    
        global_error_handler("Error in checking for updates", f"Unfortunately, there was an error in checking for updates. Please find the following error message {e}")
        
if __name__ == "__main__":
    check_for_updates()