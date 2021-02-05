from base_classes.Plugin import Plugin
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from email.mime.text import MIMEText
import base64

class NotificationPlugin(Plugin):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.notification_email = self.assistant.notification_plugin_config_dict["email"]["source"]
    self.user_email = self.assistant.notification_plugin_config_dict["email"]["destination"]

    try:
      import argparse
      self.gmail_flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
      self.gmail_flags = None

  def notify(self, notification_text):
    self.notify_email(notification_text)

  def notify_email(self, notification_text):
    credentials = self.get_gmail_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    
    b64_message = self.create_email_message(self.notification_email, self.user_email, "", notification_text)

    message = {
        "userId" : "me",
        "raw" : b64_message,
        }

    results = service.users().messages().send(userId=self.notification_email, body=message).execute()

  def create_email_message(self, sender, to, subject, message_text):
    """Create a message for an email.
    
    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.
    
    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return base64.urlsafe_b64encode(str.encode(message.as_string())).decode()


  def get_gmail_credentials(self):
    """Gets valid user credentials from storage.
  
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
  
    Returns:
      Credentials, the obtained credential.
    """
    SCOPES = "https://mail.google.com/"
    CLIENT_SECRET_FILE = "credentials/gmail_client_id.json"
    APPLICATION_NAME = "PersonalAssistant"

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
      os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                     'gmail-python-quickstart.json')
  
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
      flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
      flow.user_agent = APPLICATION_NAME
      if self.gmail_flags:
        credentials = tools.run_flow(flow, store, self.gmail_flags)
      else: # Needed only for compatibility with Python 2.6
        credentials = tools.run(flow, store)
      print('Storing credentials to ' + credential_path)
    return credentials

  def cmd_refresh_gmail_credentials(self):
    self.get_gmail_credentials()
    return True, "refreshing gmail credentials"

  def cmd_send_notification(self, notification_text):
    self.notify(notification_text)
    return True, "notified"
