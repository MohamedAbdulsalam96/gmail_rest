import frappe
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from werkzeug.middleware.proxy_fix import ProxyFix
from frappe.utils import get_url
import urllib.request

CLIENT_CONFIG = {
    "web": {
        "client_id": "717601971902-mufkvcdek70evo34uhq9r6u3up25lgm7.apps.googleusercontent.com",
        "project_id": "gleaming-cove-303805",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": [
            "https://helpdesk.frappe.cloud/oauth2callback"
        ],
        "javascript_origins": [
            "https://helpdesk.frappe.cloud"
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


@frappe.whitelist()
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri =get_url('/api/method/gmail_rest.www.home.oauth2callback')

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  frappe.session['state'] = state
  frappe.local.response['type'] = 'redirect'
  frappe.local.response['location'] = authorization_url

  return

@frappe.whitelist()
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = frappe.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES,
        state=state)
  flow.redirect_uri = get_url('/api/method/gmail_rest.www.home.oauth2callback')

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = frappe.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credential
  frappe.session['credentials'] = credentials_to_dict(credentials)
  cred=credentials_to_dict(credentials)
  print(cred)

  def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

#   return flask.redirect(flask.url_for('test_api_request'))


