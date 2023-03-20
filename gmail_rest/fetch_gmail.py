import frappe
import google.oauth2.credentials
import googleapiclient.discovery
import imaplib

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
    google_credentials=frappe.get_doc('Google Credentials')
    cred = google.oauth2.credentials.Credentials(
        token=google_credentials.token,
        refresh_token=google_credentials.refresh_token,
        token_uri=google_credentials.token_uri,
        client_id=google_credentials.client_id,
        client_secret=google_credentials.client_secret,
        scopes=['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.compose','https://www.googleapis.com/auth/gmail.send','https://www.googleapis.com/auth/gmail.modify']

    )
    gmail = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=cred)
    results = gmail.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    threads = gmail.users().threads().list(userId='me',q='is:unread').execute().get('threads', [])  
    server = imaplib.IMAP4_SSL('imap.gmail.com')
    # delimiter=','
    # string=delimiter.join(str(i) for i in threads)

    # fetch_data=frappe.get_doc({
    #     'doctype':'Fetch Data',
    #     'data':string
    # })

    # fetch_data.insert(ignore_permissions=True)
    thread_info=[]
    for thread in threads:
        thread_id = thread['id']
        thread_data = gmail.users().threads().get(userId='me', id=thread_id).execute()
        thread_info.append(thread_data)
        message = thread_data['messages'][0]
        payload = message['payload']
        headers = payload['headers']
        body=message['snippet']
        data={
            'body':body,
            'subject':'',
            'raised_by':''
        }

        for header in headers:
            try:
                if header['name'] == 'Subject':
                    data['subject'] = header['value']
            except:
                pass
            try:
                if header['name']=='Return-Path':
                    data['raised_by']=header['value']
            except:
                pass
        frappe.enqueue(create_ticket,queue='default', data=data)
        thread_data = f'''<span title=${thread['id']}>{thread['snippet']}</span>'''

    modify_request={'ids':[t['id'] for t in threads],'removeLabelIds':['UNREAD']}
    
    # try:
    #     gmail.users().messages().batchModify(userId='me', body=modify_request).execute()
    # except:
    #     frappe.throw('Email not marked as unread in gmail. An error occured')
    return thread_data

def create_ticket(data):

    ticket=frappe.get_doc({
        'doctype':'Ticket',
        'subject':data['subject'],
        'raised_by':data['raised_by'],
        'description':data['body'] 
    })
    ticket.insert(ignore_permissions=True)

def create_contact(data):
    if not frappe.db.exists('Contact',{'email_id':data['email_id']}):
        doc=frappe.get_doc({
            'doctype':'Ticket',
            'status':'Passive',
            'first_name':data['name'],
            'email_id':data['email_id']
            })
        email_id={
            'doctype':'Contact Email',
            'email_id':data['email_id']
        }
        doc.append('email_ids',email_id)

        doc.save()


