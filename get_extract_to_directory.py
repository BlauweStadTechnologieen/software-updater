from root import DIR_ROOT
import os
from error_handler import global_error_handler

def get_extract_to_directory() -> str | None:
    """
    Retrieves the base directory from the environment variable.
    Returns:
        str: The path of the base directory.
    Exceptions:
        KeyError: Raised when the DIR_ROOT environment variable is not set.
        FileNotFoundError: Raised when the specified DIR_ROOT directory does not exist.

    """
    
    try:
        
        if not DIR_ROOT:
            
            raise KeyError("DIR_ROOT environment variable is not set.")
        
        if not os.path.exists(DIR_ROOT):
            
            raise FileNotFoundError(f"The specified DIR_ROOT directory '{DIR_ROOT}' does not exist.")
                        
        return DIR_ROOT
    
    except KeyError as e:
        
        global_error_handler("Missing DIR_ROOT environment variable", f"{e}")
        
        return None
    
    except FileNotFoundError as e:
        
        global_error_handler("Invalid DIR_ROOT directory", f"The specified DIR_ROOT directory '{DIR_ROOT}' does not exist. Please check the path. {e}")
        
        return None