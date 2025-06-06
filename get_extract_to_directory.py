from root import EXTRACT_TO
import os
from error_handler import global_error_handler

def get_extract_to_directory() -> str:
    """
    Retrieves the base directory from the environment variable.
    Returns:
        str: The path of the base directory.
    Exceptions:
        KeyError: Raised when the EXTRACT_TO environment variable is not set.
        FileNotFoundError: Raised when the specified EXTRACT_TO directory does not exist.
    """
    
    try:
        
        if not EXTRACT_TO:
            
            raise KeyError("EXTRACT_TO environment variable is not set.")
        
        if not os.path.exists(EXTRACT_TO):
            
            raise FileNotFoundError(f"The specified EXTRACT_TO directory '{EXTRACT_TO}' does not exist.")
                
        return EXTRACT_TO
    
    except KeyError as e:
        
        global_error_handler("Missing EXTRACT_TO environment variable", f"{e}")
        
        return None
    
    except FileNotFoundError as e:
        
        global_error_handler("Invalid EXTRACT_TO directory", f"The specified EXTRACT_TO directory '{EXTRACT_TO}' does not exist. Please check the path. {e}")
        
        return None