import json as j
import requests as r
import os
from dotenv import load_dotenv

load_dotenv()

FRESHDESK_CREDENTIALS = {
    "FRESHDESK_DOMAIN" : os.getenv("FRESHDESK_DOMAIN"),
    "FRESHDESK_API_KEY": os.getenv("FRESHDESK_API_KEY")
}

MESSAGING_METADATA = {
    "REQUESTER_NAME" : os.getenv("REQUESTER_NAME"),
    "REQUESTER_EMAIL": os.getenv("REQUESTER_EMAIL")
}

def create_freshdesk_ticket(exception_or_error_message:str, subject:str, group_id:int = 201000039106, responder_id:int = 201002411183) -> int:
    """
    When an exception or error occurs during the execution of a function within this package, this will lodge a support toclet with Freshdesk. 
    A notification that a ticket has been created will be sent to the users email. When this function is called, it will return the ticket id.

    You will need to manually pass the exception_or_error_message and the subject parameters prior to calling the function. 

    The group_id and the responder_id parameters have been set to defaults, however, you may override these if necessary. 
    """
    
    API_URL = f'https://{FRESHDESK_CREDENTIALS["FRESHDESK_DOMAIN"]}.freshdesk.com/api/v2/tickets/'

    description = f"""
    Dear {MESSAGING_METADATA["REQUESTER_NAME"]}<br>
    A support ticket has been automatically generated because of the following error or exception message:<br><br>
    {exception_or_error_message}<br><br>
    ===================================================
    """

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
    
    try:
        response = r.post(
            API_URL,
            auth    = (FRESHDESK_CREDENTIALS["FRESHDESK_API_KEY"], 'X'),
            json    = j.dumps(ticket_data),
            timeout = 30,
            headers = {'Content-Type' : 'application/json'}
        )

    except TypeError as e:
        custom_message = f"Type Error Exception: {e}"
    
    except r.RequestException as e:
        custom_message = f"Requests Exception: {e}"

    except Exception as e:
        custom_message = f"General Exception: {e}"

    else:
    
        if response.status_code == 201:
            
            ticket_info = response.json
            ticket_id   = ticket_info.get("id")
            return ticket_id

        else:
            custom_message = f"Error code: {response.status_code} Error HTTP response: {response.text} Error response {response.content}"

    if custom_message:
        print(custom_message)
        return None