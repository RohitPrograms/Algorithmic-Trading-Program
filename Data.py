from dataclasses import dataclass

import numpy as np
from Authenticate import * 
import pandas as pd
import datetime as dt
import pandas_ta as ta
import pprint as pp

"""
This class is supposed to put all of the relevant data that we gather from
The TDA API. The necessary date we need are the following...
    
1.) Ticker Symbol
2.) Time of Candle
3.) Close of Candle
4.) Volume of Candle
5.) MACD of Candle
    i.) Actual Moving Average Convergence Divergence Line
    ii.) Signal Line (9 ema of MACD Line)
    iii.) Histogram (Difference between the MACD and Signal Line)
6.)VWAP of Candle
    i.) Volume Weighted Average Price
    ii.) VWAP + 2(std) (rolling standard deviation)
    iii.) VWAP - 2(std)
"""
ALL_PRICE_DATA = []

@dataclass
class PriceData():
    
    ticker: str
    candle_data: pd.DataFrame
    
    def __post_init__(self):
        
        cumVP = 0.0
        cumV = 0.0
        cumDiff = 0.0
        VWAP = []
        UPPER_BAND = []
        LOWER_BAND = []
        for x in range(len(self.candle_data['volume'])):
            
            cumV += self.candle_data['volume'][x]
            hlc3 = (self.candle_data['close'][x] + self.candle_data['high'][x] + self.candle_data['low'][x]) / 3
            cumVP += self.candle_data['volume'][x] * hlc3
            
            vwap = cumVP / cumV
            cumDiff += (hlc3 - vwap)**2
            vwap_std = np.sqrt(cumDiff / (x + 1))
            upper_band = vwap + (2 * vwap_std)
            lower_band = vwap - (2 * vwap_std)
            
            VWAP.append(vwap)
            UPPER_BAND.append(upper_band)
            LOWER_BAND.append(lower_band)
            
        self.candle_data['LOWER BAND'] = LOWER_BAND
        self.candle_data['VWAP'] = VWAP
        self.candle_data['UPPER BAND'] = UPPER_BAND
        
        self.candle_data.ta.macd(close='close', fast=12, slow=26, signal=9, append=True)
        self.candle_data = self.candle_data.rename(columns={ "MACDh_12_26_9": "MACD Hist",
                     "MACD_12_26_9": "MACD",
                     "MACDs_12_26_9": "Signal"})
    
    
def Get_Watchlist_Stocks():
    watchlistStocks = TDSession.get_watchlist(account = ACCT_NUMBER, watchlist_id = WATCHLIST_ID)['watchlistItems']
    Tickers = []
    for stock in range(len(watchlistStocks)):
        Tickers.append(watchlistStocks[stock]['instrument']['symbol'])
    return Tickers


def Compile_Data(watchlist, composite):
    today = dt.date.today()
    pattern = '%m/%d/%Y %H:%M:%S'

    start = dt.datetime.strftime(today, pattern) #strf = string formatter
    start = dt.datetime.strptime(start, pattern) #strp = string parser

    end = start + dt.timedelta(days = 1)

    start_epoch = str(int(round(start.timestamp() * 1000)))
    end_epoch = str(int(round(end.timestamp() * 1000))) 
    
    for stock in watchlist:
        
        data = TDSession.get_price_history(symbol = stock, 
                                   frequency_type = "minute",
                                   frequency = "5",
                                   start_date = start_epoch,
                                   end_date = end_epoch,
                                   extended_hours = "true")

        time = []
        close = []
        volume = []
        open = []
        low = []
        high = []

        for candle in range (len(data['candles'])):
            
            candle_open = float(data['candles'][candle]['open'])
            candle_high = float(data['candles'][candle]['high'])
            candle_low = float(data['candles'][candle]['low'])
            candle_close = float(data['candles'][candle]['close'])
    
            candle_time = int(data['candles'][candle]['datetime'])
            candle_volume = int(data['candles'][candle]['volume'])
    
            candle_time = dt.datetime.fromtimestamp(candle_time / 1000)
            candle_time = dt.datetime.strftime(candle_time, pattern) #strf = string formatter
    
            time.append(candle_time)
            close.append(candle_close)
            volume.append(candle_volume)
            open.append(candle_open)
            high.append(candle_high)
            low.append(candle_low)
        
        CandleData = list(zip(open, high, low, close, volume)) 
        df = pd.DataFrame(CandleData, 
                          index = time, 
                          columns = ['open', 'high', 'low', 'close', 'volume'])
        composite.append(PriceData(ticker = stock, candle_data = df))


watchlist = Get_Watchlist_Stocks()
Compile_Data(watchlist, ALL_PRICE_DATA)   
# pp.pprint(ALL_PRICE_DATA)