import frappe
import google.oauth2.credentials
import googleapiclient.discovery
import imaplib

SCOPES = []

API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

@frappe.whitelist(allow_guest=True)
def fetch():
    google_credentials=frappe.get_doc('Email Credentials')
    for scope in google_credentials.scope:
        SCOPES.append(scope.scopes)
    cred = google.oauth2.credentials.Credentials(
        token=google_credentials.token,
        refresh_token=google_credentials.refresh_token,
        token_uri=google_credentials.token_uri,
        client_id=google_credentials.client_id,
        client_secret=google_credentials.client_secret,
        scopes=SCOPES

    )
    gmail = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=cred)
    results = gmail.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    threads = gmail.users().threads().list(userId='me',q='is:unread').execute().get('threads', [])  
    server = imaplib.IMAP4_SSL('imap.gmail.com')

    thread_info=[]
    message_info=[]
    for thread in threads:
        thread_id = thread['id']
        thread_data = gmail.users().threads().get(userId='me', id=thread_id,format='full').execute()
        thread_info.append(thread_data['messages'][-1])
        message = thread_data['messages'][-1]
        thread_code=message['threadId']
        payload = message['payload']
        headers = payload['headers']
        body=message['snippet']
        data={
            'body':body,
            'subject':'',
            'raised_by':'',
            'first_name':'',
            'email':google_credentials.email,
            'message_id':'',
            'thread_id':thread_code
        }

        for msg in thread_data['messages']:
            message_id=msg['id']
            message_data = gmail.users().messages().get(userId='me', id=message_id, format='full').execute()
            message_info.append(message_data)

        for header in headers:
            try:
                if header['name'] == 'Subject':
                    data['subject'] = header['value']
            except:
                pass
            try:
                if header['name']=='Return-Path':
                    value=header['value']
                    data['raised_by']=value.replace("<","").replace(">","")
            except:
                pass
            try:
                if header['name'] == 'From':
                    value = header['value']
                    data['first_name']=value.split(' ')[0]
            except:
                pass
            try:
                if header['name']=='Message-ID':
                    value=header['value']
                    data['message_id']=value
            except:
                pass
        communications = frappe.db.get_list("Communication",filters={
        'message_id':data['message_id']
        },
        fields=['name','reference_name']
        )
        if not communications:
            frappe.enqueue(create_ticket,queue='default', data=data)
            frappe.enqueue(create_contact,queue='default',data=data)
        else:
            create_communication_thread(data=data,ticket=communications[0]['reference_name'])
        thread_data = f'''<span title=${thread['id']}>{thread['snippet']}</span>'''

    modify_request={'ids':[t['id'] for t in threads],'removeLabelIds':['UNREAD']}
    
    try:
        gmail.users().messages().batchModify(userId='me', body=modify_request).execute()
    except:
        frappe.throw('Email not marked as unread in gmail. An error occured')
    return thread_info

def create_ticket(data):

    ticket=frappe.get_doc({
        'doctype':'Ticket',
        'subject':data['subject'],
        'raised_by':data['raised_by'],
        'description':data['body'] 
    })
    ticket.insert(ignore_permissions=True)

    create_parent_communication(data=data,ticket=ticket)

def create_contact(data):
    if not frappe.db.exists('Contact',{'email_id':data['raised_by']}):
        doc=frappe.get_doc({
            'doctype':'Contact',
            'status':'Passive',
            'first_name':data['first_name'],
            })

        email_id={
            'doctype':"Contact Email",
            'email_id':data['raised_by']
        }
        doc.append("email_ids",email_id)
        doc.db_set('email_id',data['raised_by'], commit=True)
        doc.insert(ignore_permissions=True)

def create_parent_communication(data,ticket):
    communication = frappe.new_doc("Communication")
    communication.update(

		{
			"communication_type": "Communication",
			"communication_medium": "Email",
			"sent_or_received": "Received",
			"email_status": "Open",
			"subject": data['subject'],
			"sender": data['raised_by'],
			"recipients":data['email'],
			"content": data['body'],
			"status": "Linked",
            "message_id":data['message_id'],
            "thread_id":data['thread_id'],
			"reference_doctype": "Ticket",
			"reference_name": ticket.name,
		}
	)
    communication.ignore_permissions = True
    communication.ignore_mandatory = True
    communication.save(ignore_permissions=True)

def create_communication_thread(data,ticket):
    communication = frappe.new_doc("Communication")
    communication.update(
 
		{
			"communication_type": "Communication",
			"communication_medium": "Email",
			"sent_or_received": "Received",
			"email_status": "Open",
			"subject":"Re:" + data['subject'] + f" (#{ticket})",
			"sender": data['raised_by'],
			"recipients":data['email'],
			"content": data['body'],
			"status": "Linked",
			"reference_doctype": "Ticket",
			"reference_name": ticket,
		}
	)
    communication.ignore_permissions = True
    communication.ignore_mandatory = True
    communication.save(ignore_permissions=True)






