## Gmail Rest

Gmail Rest is a Frappe application that allows you to send and receive emails using REST APIs instead of the default Frappe email account setup. This README file provides instructions on how to install and configure the application.

## Installation
To install the Email Rest application, follow these steps:

1. Install Gmail Rest App
```bench get-app https://github.com/tridz-dev/gmail_rest.git```
2. Install App into your site
   ```bench --site [sitename] install-app gmail_rest```
## Configuration
To configure the email settings for Gmail Rest, follow these steps:
1. Log in to Gmail Rest application.
2. Go to the Email Credentials doctype.
3. Fill in the required information:
  Service Provider: Select "gmail" as the service provider
  ![Email Credentials](https://github.com/tridz-dev/gmail_rest/assets/73826691/34035a8d-4c03-405f-9f1d-1e43a607135a)
  
  #### Get your google cloud credentials from https://console.cloud.google.com/apis/credentials

  Fill in the required fileds as shown in images below
   ![photo1684932247](https://github.com/tridz-dev/gmail_rest/assets/73826691/5b78ca92-1e7a-422b-8dc5-85e8e2988a76)
  
    Javascript Origin is your base_url. eg: helpdesk.frappe.cloud
    Redirect uri is https://{your_base_url}/api//method/email_rest.email_rest.email.gmail.oauth.oauth2callback
  
   ![photo1684932184](https://github.com/tridz-dev/gmail_rest/assets/73826691/aac6a60e-a0e8-41b9-88d9-7becdf34d4ba)

   ![Email Credentials (3)](https://github.com/tridz-dev/gmail_rest/assets/73826691/5c7e94d9-e816-43a0-8528-029e0c8823a9)

  
  


#### License

MIT
