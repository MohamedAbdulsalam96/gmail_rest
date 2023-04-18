from __future__ import print_function
import frappe

import base64
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from frappe.core.utils import html2text

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES =[]

@frappe.whitelist()
def gmail_send_message(
    doctype=None,
    name=None,
    recipients=None,
    subject=None,
    html_content=None,
    cc=None,
    bcc=None
):
    """Create and send an email message
    Print the returned  message id
    Returns: Message object, including message id

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    google_credentials=frappe.get_doc('Email Credentials')
    doc=frappe.get_doc("Ticket",name)
    communication = frappe.new_doc("Communication")
    communication.update(
		{
			"communication_type": "Communication",
			"communication_medium": "Email",
			"sent_or_received": "Sent",
			"email_status": "Open",
			"subject": "Re: " + doc.subject + f" (#{doc.name})",
			"sender": google_credentials.email,
			"recipients": doc.raised_by,
			"content": html_content,
			"status": "Linked",
			"reference_doctype": "Ticket",
			"reference_name": doc.name,
		}
	)
    communication.ignore_permissions = True
    communication.ignore_mandatory = True
    communication.save(ignore_permissions=True)

    
    for scope in google_credentials.scope:
        SCOPES.append(scope.scopes)
    
    creds = google.oauth2.credentials.Credentials(
        token=google_credentials.token,
        refresh_token=google_credentials.refresh_token,
        token_uri=google_credentials.token_uri,
        client_id=google_credentials.client_id,
        client_secret=google_credentials.client_secret,
        scopes=SCOPES

    )
    
    parent_communication = frappe.db.get_list('Communication',filters={
        'reference_name':name
    },fields=['name','message_id','thread_id'])
    message_id=''
    thread_id=''

    for communication in parent_communication:
        if communication['message_id'] != None:
            message_id=communication['message_id']
            thread_id =communication['thread_id']
        else:
            pass

    try:
        service = build('gmail', 'v1', credentials=creds)
        plain_text_content = html2text(html_content)
        message=MIMEMultipart('alternative')
        text_part = MIMEText(plain_text_content, 'plain')
        html_part = MIMEText(html_content, 'html')

        message.attach(text_part)
        message.attach(html_part)

        message['To'] = recipients
        message['From'] = google_credentials.email
        message['Subject'] = subject
        message['Reply-To']=google_credentials.email
        message['In-Reply-To']=message_id

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message,
            'threadId':thread_id
        }
        send_message = (service.users().messages().send(userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None

    return send_message
