import frappe
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from werkzeug.middleware.proxy_fix import ProxyFix
from frappe.utils import get_url
import base64
import imaplib
import json
import urllib.request

google_credentials=frappe.get_doc('Google Credentials')

SCOPES = [
  'https://www.googleapis.com/auth/gmail.readonly',
  'https://www.googleapis.com/auth/gmail.compose',
  'https://www.googleapis.com/auth/gmail.send',
  'https://www.googleapis.com/auth/gmail.modify'
]

API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

@frappe.whitelist(allow_guest=True)
def fetch():
    cred = google.oauth2.credentials.Credentials(
        token=google_credentials.token,
        refresh_token=google_credentials.refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id='717601971902-mufkvcdek70evo34uhq9r6u3up25lgm7.apps.googleusercontent.com',
        client_secret='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',
        scopes=['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.compose','https://www.googleapis.com/auth/gmail.send','https://www.googleapis.com/auth/gmail.modify']

    )
    gmail = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=cred)
    results = gmail.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    threads = gmail.users().threads().list(userId='me',q='is:unread').execute().get('threads', [])
    server = imaplib.IMAP4_SSL('imap.gmail.com')
    
    for thread in threads:
        thread_id = thread['id']
        thread_data = gmail.users().threads().get(userId='me', id=thread_id).execute()
        message = thread_data['messages'][0]
        payload = message['payload']
        headers = payload['headers']
        subject=''

        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
                break
        

        frappe.enqueue(create_ticket,queue='default', data=subject)
        thread_data = f'''<span title=${thread['id']}>{thread['snippet']}</span>'''

    modify_request={'ids':[t['id'] for t in threads],'removeLabelIds':['UNREAD']}
    response=gmail.users().messages().batchModify(userId='me', body=modify_request).execute()
    
    return

def create_ticket(data):

    ticket=frappe.get_doc({
        'doctype':'Ticket',
        'subject':data,
        'raised_by':'user@gmail.com',
        'description':'' 
    })
    ticket.insert(ignore_permissions=True)

