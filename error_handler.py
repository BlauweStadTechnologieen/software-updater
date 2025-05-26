import freshdesk_ticket

def global_error_handler(subject:str, message:str) -> None:
    """
    Handles and processes the reporting of all error and exceptions via the Freshdesk system.
    Args:
        subject(str): Denotes the subject of the support ticket.
        message(str): Denotes the description of the error or exception. 
    """
    print(f"{subject} - {message}")
    freshdesk_ticket.create_freshdesk_ticket(message, subject)
    return
