import frappe
import google.oauth2.credentials
import google_auth_oauthlib.flow
from frappe.utils import get_url
import requests


google_credentials=frappe.get_doc('Email Credentials')
js_origin=google_credentials.javascript_origins

CLIENT_CONFIG = {
    "web": {
        "client_id": google_credentials.client_id,
        "project_id": google_credentials.project_id,
        "auth_uri": google_credentials.auth_uri,
        "token_uri": google_credentials.token_uri,
        "auth_provider_x509_cert_url": google_credentials.auth_provider_x509_cert_url,
        "client_secret": google_credentials.client_secret,
        "redirect_uris": [
            google_credentials.redirect_uri
        ],
        "javascript_origins": [
            google_credentials.javascript_origins
        ]
    }
}

SCOPES = []

for scope in google_credentials.scope:
    SCOPES.append(scope.scopes)
 

API_SERVICE_NAME = google_credentials.api_service_name
API_VERSION = google_credentials.api_version


@frappe.whitelist()
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.'
  
  flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri =get_url(f'{js_origin}/api/method/gmail_rest.gmail_rest.email.gmail.oauth.oauth2callback')

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')
  google_credentials.db_set('state',state, commit=True)

  # Store the state so the callback can verify the auth server response.


  frappe.local.response['type'] = 'redirect'
  frappe.local.response['location'] = authorization_url

  return

@frappe.whitelist()
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = google_credentials.state

  flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES,
        state=state)
  flow.redirect_uri = get_url(f'{js_origin}/api/method/gmail_rest.gmail_rest.email.gmail.oauth.oauth2callback')

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = frappe.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  frappe.session['credentials'] = credentials_to_dict(credentials)
  cred=credentials_to_dict(credentials)
  google_credentials.db_set('token',cred['token'], commit=True)
  google_credentials.db_set('refresh_token',cred['refresh_token'], commit=True) 
  frappe.local.response['type'] = 'redirect'
  frappe.local.response['location'] = '/frappedesk'
  
  return

@frappe.whitelist(allow_guest=True)
def revoke():
  credentials = google.oauth2.credentials.Credentials(
    token=google_credentials.token,
    refresh_token=google_credentials.refresh_token,
    token_uri=google_credentials.token_uri,
    client_id=google_credentials.client_id,
    client_secret=google_credentials.client_secret,
    scopes=SCOPES
  ) 
  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return frappe.throw('Credentials successfully revoked.')
  else:
    return frappe.throw('An error occurred.')

def credentials_to_dict(credentials):

  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


#   return flask.redirect(flask.url_for('test_api_request'))


 