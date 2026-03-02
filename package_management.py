from error_handler import global_error_handler
import subprocess
from subprocess import CompletedProcess
import importlib.util
import sys

#print("Script started from:", sys.argv[0])

def run_command(command:list[str], cwd:str = None) -> CompletedProcess | None:
    """
    Executes a shell command in the specified working directory.
    Args:
        command (list[str]): The command and its arguments to execute as a list of strings.
        cwd (str): The working directory in which to run the command.
    Returns:
        CompletedProcess | None: The result of the executed command as a CompletedProcess object,
        or None if the specified directory is invalid.
    Raises:
        Exception: Propagates any exception encountered during command execution after reporting it.
    Notes:
        - If the provided working directory is not valid, the function returns None.
        - Errors encountered during execution are reported using the error_handler before being raised.
    """

    try:
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)

        return result
    
    except Exception as e:

        global_error_handler.error_handler.report_error("Run Command Exception", str(e))

        return None
