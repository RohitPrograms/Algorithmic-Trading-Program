import asyncio
import pprint as pp
import datetime as dt
from websockets import client  # Fixes a bug in websockets 10

from Config import *
from Authenticate import *
from DatabaseHelpers import *


for Ticker in Watchlist_Tickers:
    CreateTimesaleTable(Ticker)
    CreateCandlestickTable(Ticker)


TDStreamingClient.timesale(service = 'TIMESALE_EQUITY', symbols= Watchlist_Tickers, fields = [0, 1, 2, 3, 4])

async def TimesalePipeline():
    await TDStreamingClient.build_pipeline()

    while True:
        data = await TDStreamingClient.start_pipeline()
        
        if 'data' in data:
            
            for timesale in data['data'][0]['content']:
                
                Ticker = timesale['key']
                trade_unix_epoch = int(timesale['1'] / 1000)
                Trade_Time = dt.datetime.fromtimestamp(trade_unix_epoch)
                Trade_Price = timesale['2']
                Trade_Volume = timesale['3']
                
                InsertIntoTimesaleTable(Ticker, Trade_Time, Trade_Price, Trade_Volume)
                AddToCandlesticks(Ticker, Trade_Time, Trade_Price, Trade_Volume)
                
                PrintCandlesticks(Ticker)
                # PrintTimesales(Ticker) 
                
                

        if False:
            await TDStreamingClient.unsubscribe(service='LEVELONE_FUTURES')
            await TDStreamingClient.close_stream()
            break

asyncio.run(TimesalePipeline())
