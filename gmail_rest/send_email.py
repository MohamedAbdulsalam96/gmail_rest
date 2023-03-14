from __future__ import print_function
import frappe

import base64
from email.message import EmailMessage

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

@frappe.whitelist()
def gmail_send_message(ticket,message,cc,bcc):
    """Create and send an email message
    Print the returned  message id
    Returns: Message object, including message id

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    ticket_doc = frappe.get_doc("Ticket", ticket)
    communication = frappe.new_doc("Communication")
    communication.update(
		{
			"communication_type": "Communication",
			"communication_medium": "Email",
			"sent_or_received": "Sent",
			"email_status": "Open",
			"subject": "Re: " + ticket_doc.subject + f" (#{ticket_doc.name})",
			"sender": frappe.session.user,
			"recipients": frappe.get_value("User", "Administrator", "email")
			if ticket_doc.raised_by == "Administrator"
			else ticket_doc.raised_by,
			"cc": cc,
			"bcc": bcc,
			"content": message,
			"status": "Linked",
			"reference_doctype": "Ticket",
			"reference_name": ticket_doc.name,
		}
	)
    communication.ignore_permissions = True
    communication.ignore_mandatory = True
    communication.save(ignore_permissions=True)


    google_credentials=frappe.get_doc('Google Credentials')
    creds = google.oauth2.credentials.Credentials(
        token=google_credentials.token,
        refresh_token=google_credentials.refresh_token,
        token_uri=google_credentials.token_uri,
        client_id=google_credentials.client_id,
        client_secret=google_credentials.client_secret,
        scopes=['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.compose','https://www.googleapis.com/auth/gmail.send','https://www.googleapis.com/auth/gmail.modify']

    )

    try:
        service = build('gmail', 'v1', credentials=creds)
        message = EmailMessage()

        message.set_content('This is automated draft mail')

        message['To'] = 'fadilsiddique@gmail.com'
        message['From'] = 'koksalfadil@gmail.com'
        message['Subject'] = 'Automated draft'

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None

    return send_message