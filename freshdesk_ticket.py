import json as j
import requests as r
import os
from dotenv import load_dotenv

load_dotenv()

FRESHDESK_CREDENTIALS = {
    "FRESHDESK_DOMAIN" : os.getenv("FRESHDESK_DOMAIN"),
    "FRESHDESK_API_KEY": os.getenv("FRESHDESK_API")
}

MESSAGING_METADATA = {
    "REQUESTER_NAME" : os.getenv("REQUESTER_NAME"),
    "REQUESTER_EMAIL": os.getenv("REQUESTER_EMAIL")
}

def validate_freshdesk_credentials() -> bool:
    """
    Checks to ensure that all FD credentiuals have been specified in the `.env` file.
    Returns:
        bool: True if all FD credentails have been specified, else it returns False.
    Exceptions:
        KeyError: Raises a KeyError is one or more FD credentials are missing.
    """
    
    try:
    
        if not FRESHDESK_CREDENTIALS["FRESHDESK_API_KEY"] or not FRESHDESK_CREDENTIALS["FRESHDESK_DOMAIN"]:
            raise KeyError("One or more Freshdesk Credentials are not specified.")
        
        if not MESSAGING_METADATA["REQUESTER_EMAIL"]:
            raise KeyError("You have no requester email specified. Please specify one now.")
    
    except KeyError as e:
        print(e)
        return False

    return True


def create_freshdesk_ticket(exception_or_error_message:str, subject:str, group_id:int = 201000039106, responder_id:int = 201002411183) -> int:
    """
    Generates a FD support ticket in the event of any error(s) generated. This is called from the `global_error_handler` method.
    Args:
        exception_or_error_message(str): Denotes the description of the error or exception message.
        subject(str): Denotes the subject of the error or exception message.
        group_id(int, optional): Denotes the Department to whom the error or exception of relates to.
        responder_id(int, optional): Denotes the individual in the department to whom the error or exception related to.
    Returns:
        ticket_id(str): Returns the ID of the ticket if the script succeeds, else it returns `None`
    Raises:
        RequestException: Raises a `RequestException` if the API request fails.
        Exception: Raises an `Exception` is any other error other than an`RequestException` error occours.

    """
    
    if not validate_freshdesk_credentials():
                
        return
    
    API_URL = f'https://{FRESHDESK_CREDENTIALS["FRESHDESK_DOMAIN"]}.freshdesk.com/api/v2/tickets/'

    description = f"""
    Dear {MESSAGING_METADATA["REQUESTER_NAME"]}<br>
    A support ticket has been automatically generated because of the following error or exception message:<br><br>
    {exception_or_error_message}<br><br>
    ===================================================
    """
    try:

        ticket_data = {
            "subject"     : subject,
            "description" : description, 
            'priority'    : 1,
            'status'      : 2,
            'group_id'    : group_id,
            'responder_id': responder_id,
            'requester'   : {
                'name'    : MESSAGING_METADATA["REQUESTER_NAME"],
                'email'   : MESSAGING_METADATA["REQUESTER_EMAIL"]
            } 
        }

        custom_message  = None
        ticket_id       = None
    
        response = r.post(
            API_URL,
            auth    = (FRESHDESK_CREDENTIALS["FRESHDESK_API_KEY"], 'X'),
            json    = j.dumps(ticket_data),
            timeout = 30,
            headers = {'Content-Type' : 'application/json'}
        )

        if response.status_code == 201:
            
            ticket_info = response.json
            ticket_id   = ticket_info.get("id")
            return ticket_id

        else:
            custom_message = f"Error code: {response.status_code} Error HTTP response: {response.text} Error response {response.content}"
            print(custom_message)
            return response.status_code

    except r.RequestException as e:
        custom_message = f"Requests Exception: {e}"

    except Exception as e:
        custom_message = f"General Exception: {e}"
    
    print(custom_message)
    return -1