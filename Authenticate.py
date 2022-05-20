from td.client import TDClient
from Config import *

TDSession = TDClient(client_id = CONSUMER_KEY, 
                         redirect_uri = REDIRECT_URL,
                         credentials_path = CREDENTIALS_PATH)
TDSession.login()