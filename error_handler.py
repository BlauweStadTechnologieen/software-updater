import freshdesk_ticket

def handle_error(message:str, subject:str) -> bool:
    print(f"{message} {subject}")
    freshdesk_ticket.create_freshdesk_ticket(message, subject)
    return False