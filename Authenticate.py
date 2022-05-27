from td.client import TDClient
from Config import *

# Initializing the TD Session
TDSession = TDClient(client_id = CONSUMER_KEY, 
                         redirect_uri = REDIRECT_URL,
                         credentials_path = CREDENTIALS_PATH)
TDSession.login()

# Initializing the TD Streaming Session
TDStreamingClient = TDSession.create_streaming_session()

# Gathering the Ticker Symbols From a Speicifed Watchlist
def Get_Watchlist_Stocks():
    watchlistStocks = TDSession.get_watchlist(account = ACCT_NUMBER, watchlist_id = WATCHLIST_ID)['watchlistItems']
    Tickers = []
    for stock in range(len(watchlistStocks)):
        Tickers.append(watchlistStocks[stock]['instrument']['symbol'])
    return Tickers

Watchlist_Tickers = ['/ES', '/MES']
# Watchlist_Tickers = Get_Watchlist_Stocks()