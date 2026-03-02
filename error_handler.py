import logging
import sys

def global_error_handler(subject:str, message:str, logging_level = logging.INFO) -> None:
    """
    Handles and processes the reporting of all error and exceptions via the Freshdesk system.
    Args:
        subject(str): Denotes the subject of the support ticket.
        message(str): Denotes the description of the error or exception. 
    """

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(

        level=logging_level,
        filename="log.log",
        filemode='a',
        format='%(levelname)s: %(message)s'

    )

    log_message = f"{subject} - {message}"

    logging.log(logging_level, log_message)

    return None


def missing_keys(dictionary:dict[str:str]):
    
    missing = []
    
    for key, value in dictionary.items():
        
        if not value:
            
            missing.append(key)
    
    if missing:

        print(f"Missing keys: {', '.join(missing)}")

        sys.exit()

    return dictionary


if __name__ == "__main__":
    global_error_handler("Test Subject", "Test Message", logging_level=logging.DEBUG)