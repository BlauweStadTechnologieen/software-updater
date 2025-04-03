import freshdesk_ticket

def global_error_handler(subject:str, message:str) -> bool:
    print(f"{subject} - {message}")
    freshdesk_ticket.create_freshdesk_ticket(message, subject)
    return False

def generate_support_ticket(subject:str, message:str) -> None:
    freshdesk_ticket.create_freshdesk_ticket(message, subject)
    return