import hashlib
import subprocess
import os
import error_handler

def check_and_install_new_dependencies(requirements_file:str ="requirements.txt", hash_file=".requirements_hash") -> None:
    """
    After it checks for the existece of the file denoted in the `requreiments_file` arguement, it then checks for changes in requirements.txt file and installs dependencies if changes are detected. This is achieved by detetching any changes in the `current_hash` file. If this differt from the previous hash, it executes the script.

    Args:
        requirements_file(str, optional): Denoted the name of the file containing the updated list of dependancies.
        .requirements_has(str, optional): Denotes the name of the file containg the has of the latest commit.
    Notes:
    -
    Should an error be detected, the `error_handler` module is called, when will process the error and generate a support ticket, which is then sent to tee relevant department.
    
    """
    def compute_hash(file_path):
        """Computes the hash of a file."""
        with open(file_path, "rb") as f:
            content = f.read()
            return hashlib.sha256(content).hexdigest()

    # Check if requirements.txt exists
    if not os.path.exists(requirements_file):
        custom_message = f"{requirements_file} not found!"
        custom_subject = "Requirements.txt file not found"
        error_handler.global_error_handler(custom_subject, custom_message)
        return

    # Compute the current hash of requirements.txt
    current_hash = compute_hash(requirements_file)

    # Read the stored hash if it exists
    stored_hash = None
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            stored_hash = f.read().strip()

    # Compare hashes and install dependencies if there are changes
    if current_hash != stored_hash:
        print("Changes detected in requirements.txt. Installing dependencies...")
        try:
            subprocess.run(["pip", "install", "-r", requirements_file])
            # Update the stored hash
            with open(hash_file, "w") as f:
                f.write(current_hash)
            print("Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            custom_message = f"Failed to install dependencies: {e}"
            custom_subject = "Dependancy installation failure"
            error_handler.global_error_handler(custom_subject, custom_message)
            return