import frappe
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from werkzeug.middleware.proxy_fix import ProxyFix
from frappe.utils import get_url
import imaplib
import json
import urllib.request

# credentials={

#     'token': 'ya29.a0AVvZVsonNvi1Drd6bcHwgRyi0BEwRg_lZtqHeGGN0BRLUoQJdKi_vy3gLrmi0tby3jOp157Eao7nqpcnu8aop7qPVb0_M5OkMZmR6gyxDXWHdDNHPLh4fRrICtsEE9TZGYoXJsVPJrRldB4viVH9irFF3Z5XaCgYKAZ0SARISFQGbdwaItHcvWMrbhNvgFnlTaB3-iQ0163',
#     'refresh_token': '1//0gO6q6L0upOIxCgYIARAAGBASNwF-L9IrpkwqGOzca7zvRmI7-wIf930ijwf9kjf7kqbCKrBq5vxGbpX7-xM1HIJS4wkLLqwI87M',
#     'token_uri': 'https://oauth2.googleapis.com/token',
#     'client_id': '717601971902-mufkvcdek70evo34uhq9r6u3up25lgm7.apps.googleusercontent.com',
#     'client_secret': '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',
#     'scopes': [
#         'https://www.googleapis.com/auth/gmail.readonly',
#         'https://www.googleapis.com/auth/gmail.compose',
#         'https://www.googleapis.com/auth/gmail.send'
#   ]
# }

CLIENT_CONFIG = {
    "web": {
        "client_id": "717601971902-mufkvcdek70evo34uhq9r6u3up25lgm7.apps.googleusercontent.com",
        "project_id": "gleaming-cove-303805",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": [
            "https://desk.tridz.in/oauth2callback"
        ],
        "javascript_origins": [
            "https://desk.tridz.in"
        ]
    }
}

SCOPES = [
  'https://www.googleapis.com/auth/gmail.readonly',
  'https://www.googleapis.com/auth/gmail.compose',
  'https://www.googleapis.com/auth/gmail.send',
]

API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

@frappe.whitelist(allow_guest=True)
def fetch():

    cred = google.oauth2.credentials.Credentials(
        token='ya29.a0AVvZVspcJPjTdJQsy64-o764hD656qsiG8DyM-7hZBB8HZfepQwWaLSfBTj2-219s0mDX8y2pQ9aWfhZWber_5Gwiv-JEjOwcYzhywSqSa3ECiVvMU5vPi62wzTWgukSlxNofBQSrdZ784NEZLyNAWwaEzw_aCgYKAQsSARISFQGbdwaIpYfQgAzrjzuOCWI4N4AppQ0163',
        refresh_token='1//0g1B4zMLv1RrLCgYIARAAGBASNwF-L9IrRDb2dRAK3_ezw2sFlk1q2oJVAlUgZ4M4ebo-hIz-m1lfNzOccbefnALWSPjoKBzHC7Y',
        token_uri='https://oauth2.googleapis.com/token',
        client_id='717601971902-mufkvcdek70evo34uhq9r6u3up25lgm7.apps.googleusercontent.com',
        client_secret='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',
        scopes=['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.compose','https://www.googleapis.com/auth/gmail.send']

    )
    gmail = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=cred)
    results = gmail.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    threads = gmail.users().threads().list(userId='me').execute().get('threads', [])
    server = imaplib.IMAP4_SSL('imap.gmail.com')

    email_data = ""
    email_data +="""
    <style>
     h2, body {
      font-family:Helvetica,sans-serif;      
     }
     
    </style>
    <div style='border:solid 1px #c3c3c3;width:70%; margin:20px auto'>
    <h2 style='margin-left:20px'>Emails Threads</h2>
    """

    for thread in threads:
        thread_data = f'''<span title=${thread['id']}>{thread['snippet']}</span>'''
        email_data +=f'''<div style='border-bottom:solid 1px #c3c3c3; padding: 20px 10px;'><div style='padding:10px;margin-bottom:10px'>  <input type="checkbox">{thread_data} </div></div>'''

        frappe.get_doc(
            {
                "doctype":"Ticket",
                "subject":thread['id'],
                "raised_by":"fadilsiddique@gmail.com",
            }
        ).insert(ignore_permissions=True)
    email_data +="</div>"

    return frappe.render_template(email_data,context={})