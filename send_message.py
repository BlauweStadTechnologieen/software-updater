import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import freshdesk_ticket as fd

load_dotenv()

MESSAGING_METADATA = {
    "REQUESTER_NAME"        : os.getenv("REQUESTER_NAME"),
    "REQUESTER_EMAIL"       : os.getenv("REQUESTER_EMAIL"),
    "SMTP_SERVER"           : os.getenv("SMTP_SERVER"),
    "SMTP_EMAIL"            : os.getenv("SMTP_EMAIL"),
    "SMTP_PASSWORD"         : os.getenv("SMTP_PASSWORD"),
    "SMTP_PORT"             : os.getenv("SMTP_PORT"),
    "SENDER_NAME"           : os.getenv("SENDER_NAME"),
    "SENDER_EMAIL"          : os.getenv("SENDER_EMAIL"),
    "SENDER_DEPARTMENT"     : os.getenv("SENDER_DEPARTMENT")
}

def company_signoff() -> None:
    return f"""
    If you have any issues or concerns, please get in contact us with us on the email address below.<br>
    Yours sincerely<br>
    <b>{MESSAGING_METADATA["SENDER_NAME"]}</b><br>
    The {MESSAGING_METADATA['SENDER_DEPARTMENT']} Team<br>
    """

def send_message(software_updates:list, mime_type:str = "html") -> None:
    
    updated_software_packages_list = ""
    
    for software_update in software_updates:
        
        updated_software_packages_list += f"""
        <table border="0" cellpadding="5" cellspacing="0" style="border-collapse: collapse; text-align: left;">
            <tr>
                <td style="padding-left:0px"><b>{software_update}</b></td>
            </tr>
        </table>
        """
            
    message_body = f"""
    Dear {MESSAGING_METADATA["REQUESTER_NAME"]}<br><br>
    You have new updates to the following software packages.<br><br>
    {updated_software_packages_list}<br>
    * You must be logged into the GitHub Repository in order to see the list of commits within the API call.<br><br>
    {company_signoff()}<br><br>
    """
    msg             = MIMEMultipart()
    msg['Subject']  = "Updated Software Packages"
    msg['From']     = f'"{MESSAGING_METADATA["SENDER_NAME"]}" <{MESSAGING_METADATA["SENDER_EMAIL"]}>'
    msg['To']       = MESSAGING_METADATA["REQUESTER_EMAIL"]
    body            = message_body
    msg.attach(MIMEText(body, mime_type))

    try:
        with smtplib.SMTP(MESSAGING_METADATA["SMTP_SERVER"], MESSAGING_METADATA["SMTP_PORT"]) as server:

            server.starttls()

            server.login(MESSAGING_METADATA["SMTP_EMAIL"], 
                         MESSAGING_METADATA["SMTP_PASSWORD"]
            )
            server.sendmail(MESSAGING_METADATA["SENDER_EMAIL"],
                            MESSAGING_METADATA["REQUESTER_EMAIL"], 
                            msg.as_string()
            )

            return True
        
    except Exception as e:

        custom_message = f"Error sending email: {e}"
        custom_subject  = "SMTP Authentication Error"

        print(custom_subject)
        print(custom_message)

        fd.create_freshdesk_ticket(custom_message,custom_subject)

        return False