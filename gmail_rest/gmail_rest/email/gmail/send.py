from __future__ import print_function
import frappe

import base64
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
    content=None,
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
			"content": content,
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
    },fields=['name','message_id'])
    message_id=''

    for communication in parent_communication:
        if communication['message_id'] != None:
            message_id=communication['message_id']
        else:
            pass

    try:
        service = build('gmail', 'v1', credentials=creds)
        message = EmailMessage()

        message.set_content(content)

        message['To'] = recipients
        message['From'] = google_credentials.email
        message['Subject'] = subject
        message['Reply-To']=google_credentials.email
        message['In-Reply-To']=message_id
        message['References']=message_id

  
        # threads = service.users().threads().list(
        #     userId='me', q='subject:"{}"'.format(subject)).execute().get('threads', [])

        # thread_id = threads[0]['threadId'] if threads else None

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message,
        }
        # pylint: disable=E1101
        # try:
        #     service.users().threads().list(userId='me', q='subject:"{}"'.format(subject)).execute().get('threads', [])
        # except:
        #     pass
        send_message = (service.users().messages().send(userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None

    return send_message
