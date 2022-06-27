from asyncio.windows_events import NULL
import Price
import TechnicalAnalysis as ta
import sqlite3 as sq
from Authenticate import *
import datetime as dt

# These are the defintions we will use to determine position entries / exits

    # The Buy Conditions:
        # 1.) The ADX should be above 25, signaling a strong trend.
        # 2.) There should be a crossover of the +DI and -DI 
            # If the DI+ is greater after the crossover, we are bullish
            # If the DI- is greater after the crossover, we are bearish
    
    # The Sell Conditions:
        # 1.) A crossover in the other direction occurs
        # 2.) ADX drops below 25
        

# We want to store these signals in a separate database, and use this 
# database to facilitate our equity orders.

ADX_Threshold = 25

def CreateSignalsTable():
# Creating the Database that holds all f our signals, which we will read from to create orders.
    
    Query = ("CREATE TABLE IF NOT EXISTS Signals" 
             " ( Ticker TEXT NOT NULL, " + 
             "TradeTime TEXT NOT NULL, " +
             "PositionType TEXT NOT NULL, " + 
             "TradePrice FLOAT NOT NULL, " +
             "StopLoss FLOAT NOT NULL" + ");")
    
    cursor.execute(Query)
    

def ADXConfimation(Ticker: str, Trade_Time: dt.datetime):

# ADXConfirmation only returns true when the most recent ADX value is above the specified threshhold value, and the
    # most recent ADX value is greater than its preceding ADX value. 
    
    RecentFullCandle = Price.OHLCV(Ticker, Trade_Time - dt.timedelta(minutes = Price.CANDLESTICK_INTERVAL))
    PreviousFullCanlde = Price.OHLCV(Ticker, Trade_Time - dt.timedelta(minutes = 2 * Price.CANDLESTICK_INTERVAL))
    
    if (RecentFullCandle != None) and (PreviousFullCanlde != None):
        
        if ((ta.ADX(Ticker, Trade_Time - dt.timedelta(minutes = Price.CANDLESTICK_INTERVAL), 14) != NULL) and
            (ta.ADX(Ticker, Trade_Time - dt.timedelta(minutes = 2 * Price.CANDLESTICK_INTERVAL), 14) != NULL)) :
            
            RecentADX = ta.ADX(Ticker, Trade_Time - dt.timedelta(minutes = Price.CANDLESTICK_INTERVAL), 14)
            PreviousADX = ta.ADX(Ticker, Trade_Time - dt.timedelta(minutes = 2 * Price.CANDLESTICK_INTERVAL), 14)
            
            if (RecentADX > ADX_Threshold) and (RecentADX > PreviousADX):
                return True
    
    return False


def DICrossoverType(Ticker: str, Trade_Time: dt.datetime):

# Returns a string "Short", "Long", or "None"

    # "Short": The -DI crosses over the +DI. This means that during the most recent candlestick, -DI > +DI, and during the  
        # candlestick before that, +DI > -DI.
    
    # "Long": The +DI crosses over the -DI. This means that during the most recent candlestick, +DI > -DI, and during the  
        # candlestick before that, -DI > +DI.
    
    # "None": No type of crossover occurs. That means that during the most recent candlestick and the candlestick before, either
        # +DI > -DI or -DI > +DI.
    
    RecentFullCandle = Price.OHLCV(Ticker, Trade_Time - dt.timedelta(minutes = Price.CANDLESTICK_INTERVAL))
    PreviousFullCanlde = Price.OHLCV(Ticker, Trade_Time - dt.timedelta(minutes = 2 * Price.CANDLESTICK_INTERVAL))
    
    if (RecentFullCandle != None) and (PreviousFullCanlde != None):
        
        if ((ta.PlusDI(Ticker, Trade_Time - dt.timedelta(minutes = Price.CANDLESTICK_INTERVAL), 14) != NULL) and
            (ta.PlusDI(Ticker, Trade_Time - dt.timedelta(minutes = 2 * Price.CANDLESTICK_INTERVAL), 14) != NULL)):
                
                RecentPlusDI = ta.PlusDI(Ticker, Trade_Time - dt.timedelta(minutes = Price.CANDLESTICK_INTERVAL), 14)
                RecentMinusDI = ta.MinusDI(Ticker, Trade_Time - dt.timedelta(minutes = Price.CANDLESTICK_INTERVAL), 14)
                
                PreviousPlusDI = ta.PlusDI(Ticker, Trade_Time - dt.timedelta(minutes = 2 * Price.CANDLESTICK_INTERVAL), 14)
                PreviousMinusDI = ta.MinusDI(Ticker,Trade_Time - dt.timedelta(minutes = 2 * Price.CANDLESTICK_INTERVAL), 14)
                
                if (PreviousPlusDI > PreviousMinusDI) and (RecentPlusDI < RecentMinusDI):
                    return "Short" 
                
                elif (PreviousPlusDI < PreviousMinusDI) and (RecentPlusDI > RecentMinusDI):
                    return "Long" 
    
    return "None"
    
def AddSignal(Ticker: str, Trade_Time: dt.datetime):
    
    # We want to add a signal to our signals table once there some type of DI crossover, and there is also a confirmation from the ADX.
    
    RecentFullCandle = Price.OHLCV(Ticker, Trade_Time - dt.timedelta(minutes = Price.CANDLESTICK_INTERVAL))
    
    if(RecentFullCandle != None):
        Length = abs(RecentFullCandle["High"] - RecentFullCandle["Low"])
        TradePrice = RecentFullCandle["Close"]
    
    # If ADXConfirmation is True, and the CrossoverType was Long, that would mean that we should take a long position.
        # The stop-loss is equivalent to the trade price minus the length of the candle during which the signal was created.
    if (ADXConfimation(Ticker, Trade_Time) == True) and (DICrossoverType(Ticker, Trade_Time) == "Long"):
        
        Query = ("INSERT INTO Signals"  + 
                 " (Ticker, TradeTime, PositionType, TradePrice, StopLoss, TakeProfit) VALUES ( '" + 
                 str(Ticker) + "', '" + 
                 str(Trade_Time) + "', " + 
                 str(DICrossoverType(Ticker, Trade_Time)) + "', " + 
                 str(TradePrice) + "', " + 
                 str(TradePrice - Length) + " );")
        cursor.execute(Query) 
    
    # If ADXConfirmation is True, and the CrossoverType was Short, that would mean that we should take a short position.
        # The stop-loss is equivalent to the trade price plus the length of the candle during which the signal was created.
    elif (ADXConfimation(Ticker, Trade_Time) == True) and (DICrossoverType(Ticker, Trade_Time) == "Short"):
        
        Query = ("INSERT INTO Signals"  + 
                 " (Ticker, TradeTime, PositionType, TradePrice, StopLoss, TakeProfit) VALUES ( '" + 
                 str(Ticker) + "', '" + 
                 str(Trade_Time) + "', " + 
                 str(DICrossoverType(Ticker, Trade_Time)) + "', " + 
                 str(TradePrice) + "', " + 
                 str(TradePrice + Length) + " );")
        cursor.execute(Query) 

def PrintSignals():
    
    Query = "SELECT * FROM Signals"
    cursor.execute(Query)
    print(cursor.fetchall())
    