import hashlib
import subprocess
import os

def check_and_install_new_dependancies(requirements_file="requirements.txt", hash_file=".requirements_hash") -> None:
    """
    Checks for changes in requirements.txt and installs dependencies if changes are detected.

    It is essential that this is executed in your .venv. This is handled through the .BAT file which activated the .venv
    before running the script which calles this function.

    :param requirements_file: Path to the requirements.txt file
    :param hash_file: Path to the file storing the previous hash
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
        print(f"{requirements_file} not found!")
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
            print(f"Failed to install dependencies: {e} {custom_message}{custom_subject}")