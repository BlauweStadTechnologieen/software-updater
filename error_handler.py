import freshdesk_ticket
import logging
import sys

def global_error_handler(subject:str, message:str, logging_level = logging.DEBUG, file_log = "log" ) -> None:
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
        filename=file_log,
        filemode='a',
        format='%(levelname)s: %(message)s'

    )

    log_message = f"{subject} - {message}"

    logging.log(logging_level, log_message)

    if logging_level <= logging.WARNING:

        return None
    
    if logging_level >= logging.ERROR:

        freshdesk_ticket.create_freshdesk_ticket(message, subject)

        sys.exit(f"The script has encountered a {logging_level} incident, & will now exit. Please check the error log for details.")

def missing_keys(dictionary:dict[str:str]):
    
    missing = []
    
    for key, value in dictionary.items():
        
        if not value:
            
            missing.append(key)
    
    if missing:

        print(f"Missing keys: {', '.join(missing)}")

        sys.exit()

    return dictionary