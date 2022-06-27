from asyncio.windows_events import NULL
import TechnicalAnalysis as ta
import sqlite3 as sq
import pprint as pp
import datetime as dt
from Authenticate import *

#------------------------------------------------------------------------------------------

# Essential variables to interact with the AlgoData Database



#------------------------------------------------------------------------------------------

# The time frequency at which we want to create new candlesticks (in minutes)

CANDLESTICK_INTERVAL = 1

#------------------------------------------------------------------------------------------

# Dynamically Creating a table for each Ticker Symbol

    # For example, the Table Name for SPY would be SPYCandles
    
    # These tables are meant to store the candlesticks for each stock, as well as 
    # the DMI, ADX, and VWAP
    
def CreateCandlestickTable(Ticker):
    
    TableName = Ticker.replace("/", "")
    TableName += "Candles"
    
    Query = ("CREATE TABLE IF NOT EXISTS " + TableName + 
             " ( Ticker TEXT NOT NULL, " + 
             "CandleTime TEXT NOT NULL, " + 
             "Open FLOAT NOT NULL, " + 
             "High FLOAT NOT NULL, " + 
             "Low FLOAT NOT NULL, " + 
             "Close FLOAT NOT NULL, " + 
             "Volume FLOAT NOT NULL, " +
             "TrueRange FLOAT, " +
             "ATR FLOAT, " +
             "PlusDM FLOAT, " +
             "MinusDM FLOAT, " +
             "PlusDI FLOAT, " +
             "MinusDI FLOAT, " +
             "ADX FLOAT " + ");")
    
    cursor.execute(Query)

#------------------------------------------------------------------------------------------

# Round the time based on the Candlestick interval

# For example, if we were using 5-minute candlesticks and we passed in 12:34:56, this method
# would return 12:30:00  
    
def GetFlooredTime(Time: dt.datetime):
    
    total_minutes = (60 * (Time.hour)) + Time.minute
    minutes_to_subtract = total_minutes % CANDLESTICK_INTERVAL
    FlooredTime = Time - dt.timedelta(minutes = minutes_to_subtract, seconds = Time.second)
    return FlooredTime


#------------------------------------------------------------------------------------------

# Retrieves the name of table that a ticker's candlestick data is stored in.

def GetTableName(Ticker: str):
    
    TableName = Ticker.replace("/", "")
    TableName += "Candles"
    return TableName

#------------------------------------------------------------------------------------------

# Returns the Open, High, Low, Close, and Volume for the given ticker and time as a
# dictionary.

def OHLCV(Ticker: str, Trade_Time: dt.datetime):
    
    TableName = GetTableName(Ticker)
    
    Candle =  ("SELECT * FROM " + TableName + 
                         " WHERE CandleTime = '" + 
                         str(GetFlooredTime(Trade_Time)) + "';")
    cursor.execute(Candle)
    temp = str(cursor.fetchall())
    temp = temp.replace("[", "")
    temp = temp.replace("]", "")
    temp = temp.replace("(", "")
    temp = temp.replace(")", "")
    
    Dictionary = {}
    
    if (len(temp) != 0):
        
        CandleInfo = temp.split(",") 
        Dictionary.update({"Ticker" : CandleInfo[0]})
        Dictionary.update({"Candle Time" : CandleInfo[1]})
        Dictionary.update({"Open" : float(CandleInfo[2])})
        Dictionary.update({"High" : float(CandleInfo[3])})
        Dictionary.update({"Low" : float(CandleInfo[4])})
        Dictionary.update({"Close" : float(CandleInfo[5])})
        Dictionary.update({"Volume" : float(CandleInfo[6])})
        
        return Dictionary
    
    return None

#------------------------------------------------------------------------------------------

# Printing the Candlestick Data for the given data to the console

def PrintCandlesticks(Ticker):
    
    TableName = GetTableName(Ticker)
    print("Ticker | Time | DMI+ | DMI- | ADX | Volume")
    Query = "SELECT Ticker, CandleTime, PlusDI, MinusDI, ADX, Volume FROM " + TableName
    cursor.execute(Query)
    pp.pprint(cursor.fetchall())
    
#------------------------------------------------------------------------------------------

# Updates the candlestick data and technical analysis values
# based on the values we get from each timesale 

# If the candlestick doesn't exist, we create a new candlestick

def Update(Ticker, Trade_Time, Trade_Price, Trade_Volume):
    
    CurrentCandle = OHLCV(Ticker, Trade_Time)
    
    if (CurrentCandle == None):
        
        Query = ("INSERT INTO " + GetTableName(Ticker) + 
                 " (Ticker, CandleTime, Open, High, Low, Close, Volume, TrueRange, ATR, PlusDM, MinusDM, PlusDI, MinusDI, ADX) VALUES ( '" + 
                 str(Ticker) + "', '" + 
                 str(GetFlooredTime(Trade_Time)) + "', " + 
                 str(Trade_Price) + ", "  + 
                 str(Trade_Price) + ", "  + 
                 str(Trade_Price) + ", "  + 
                 str(Trade_Price) + ", "  + 
                 str(Trade_Volume) + ", "  + 
                 str(ta.TrueRange(Ticker, Trade_Time)) + ", " + 
                 str(ta.ATR(Ticker, Trade_Time, 14)) + ", " +
                 str(ta.PlusDM(Ticker, Trade_Time)) + ", " +
                 str(ta.MinusDM(Ticker, Trade_Time)) + ", " +
                 str(ta.PlusDI(Ticker, Trade_Time, 14)) + ", " +
                 str(ta.MinusDI(Ticker, Trade_Time, 14)) + ", " +
                 str(ta.ADX(Ticker, Trade_Time, 14)) + " );")
    
        cursor.execute(Query) 
    
    else:
        
        CurrentHigh = CurrentCandle["High"]
        CurrentLow = CurrentCandle["Low"]
        CurrentVolume = CurrentCandle["Volume"]
        
        if Trade_Price > CurrentHigh:
            CurrentHigh = Trade_Price
        
        if Trade_Price < CurrentLow:
            CurrentLow = Trade_Price
        
        CurrentVolume += Trade_Volume
        
        Query = ("UPDATE " + GetTableName(Ticker) + 
                 " SET High = " + str(CurrentHigh) + 
                 ", Low = " + str(CurrentLow) + 
                 ", Volume = " + str(CurrentVolume) + 
                 ", Close = " + str(Trade_Price) + 
                 " WHERE CandleTime = '" + str(GetFlooredTime(Trade_Time)) + "';")
        cursor.execute(Query)
        
        Query =  ("UPDATE " + GetTableName(Ticker) + 
                 " SET TrueRange = " + str(ta.TrueRange(Ticker, Trade_Time)) + 
                " WHERE CandleTime = '" + str(GetFlooredTime(Trade_Time)) + "';")
        cursor.execute(Query)
        
        Query = ("UPDATE " + GetTableName(Ticker) + 
                 " SET ATR = " + str(ta.ATR(Ticker, Trade_Time, 14)) + 
                " WHERE CandleTime = '" + str(GetFlooredTime(Trade_Time)) + "';")      
        cursor.execute(Query)
        
        Query = ("UPDATE " + GetTableName(Ticker) + 
                 " SET PlusDM = " + str(ta.PlusDM(Ticker, Trade_Time)) + 
                 ", MinusDM = " + str(ta.MinusDM(Ticker, Trade_Time)) + 
                 " WHERE CandleTime = '" + str(GetFlooredTime(Trade_Time)) + "';")
        cursor.execute(Query)
        
        Query = ("UPDATE " + GetTableName(Ticker) + 
                 " SET PlusDI = " + str(ta.PlusDI(Ticker, Trade_Time, 14)) + 
                 ", MinusDI = " + str(ta.MinusDI(Ticker, Trade_Time, 14)) + 
                 " WHERE CandleTime = '" + str(GetFlooredTime(Trade_Time)) + "';")
        cursor.execute(Query)
        
        Query = ("UPDATE " + GetTableName(Ticker) + 
                 " SET ADX = " + str(ta.ADX(Ticker, Trade_Time, 14)) + 
                 " WHERE CandleTime = '" + str(GetFlooredTime(Trade_Time)) + "';")
        cursor.execute(Query)

