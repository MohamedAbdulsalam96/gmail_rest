from gmail_rest.gmail_rest.email.gmail.send import gmail_send_message
import frappe

def sendmail(
    doctype=None,
    name=None,
    recipients=None,
    subject=None,
    content=None,
    cc=None,
    bcc=None
):
    email_settings = frappe.get_doc('Email Credentials')
    if email_settings.service_provider == 'gmail':
        gmail_send_message(
            doctype=doctype,
            name=name,
            recipients=recipients,
            subject=subject,
            content=content,
            cc=cc,
            bcc=bcc
        )
    elif email_settings.service_provider == None:
        frappe.throw("Setup Email Account")
