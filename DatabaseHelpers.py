import sqlite3 as sq
import pprint as pp
import datetime as dt

DB_Connection = sq.connect("AlgoData.db")
DB_Cursor = DB_Connection.cursor()

cursor = DB_Connection.cursor()


def CreateTimesaleTable(Ticker):
    
    TableName = Ticker.replace("/", "")
    TableName += "Timesales"
    
    Query = "CREATE TABLE IF NOT EXISTS " + TableName + " ( Ticker TEXT NOT NULL, TradeTime TEXT NOT NULL, TradePrice FLOAT NOT NULL, TradeVolume FLOAT NOT NULL);"
    cursor.execute(Query)


def InsertIntoTimesaleTable(Ticker, Time, Price, Volume):
    
    TableName = Ticker.replace("/", "")
    TableName += "Timesales"
    
    Query = "INSERT INTO " + TableName + " (Ticker, TradeTime, TradePrice, TradeVolume) VALUES ('" + str(Ticker) + "', '" + str(Time) + "', " + str(Price) +  ", " +  str(Volume) + ");"
    cursor.execute(Query)



def PrintTimesales(Ticker):
    
    TableName = Ticker.replace("/", "")
    TableName += "Timesales"
    
    Query = "SELECT * FROM " + TableName
    cursor.execute(Query)
    pp.pprint(cursor.fetchall())
    

def CreateCandlestickTable(Ticker):
    TableName = Ticker.replace("/", "")
    TableName += "Candles"
    
    Query = "CREATE TABLE IF NOT EXISTS " + TableName + " ( Ticker TEXT NOT NULL, CandleTime TEXT NOT NULL, Open FLOAT, High FLOAT, Low FLOAT, Close FLOAT, Volume FLOAT );"
    cursor.execute(Query)
    
        
def AddToCandlesticks(Ticker, Trade_Time, Trade_Price, Trade_Volume):
    
    total_minutes = (60 * (Trade_Time.hour)) + Trade_Time.minute
    minutes_to_subtract = total_minutes % 5
    FlooredTime = Trade_Time - dt.timedelta(minutes = minutes_to_subtract, seconds = Trade_Time.second)
        
    TableName = Ticker.replace("/", "")
    TableName += "Candles"
    
    GetAllCandleTimes = "SELECT CandleTime FROM " + TableName + " WHERE CandleTime = '" + str(FlooredTime) + "';"
    cursor.execute(GetAllCandleTimes)
    AllCandleTimes = cursor.fetchall()
    
    if (len(AllCandleTimes) == 0):
        print("Creating New CandleStick")
        Query = "INSERT INTO " + TableName + " (Ticker, CandleTime, Open, High, Low, Close, Volume) VALUES ( '" + str(Ticker) + "', '" + str(FlooredTime) + "', " + str(Trade_Price) + ", "  + str(Trade_Price) + ", "  + str(Trade_Price) + ", "  + str(Trade_Price) + ", "  + str(Trade_Volume) +  " );"
        print(Query)
        cursor.execute(Query) 
    
    else:
        GetCurrentHLV = "SELECT High, Low, Volume FROM " + TableName + " WHERE CandleTime = '" + str(FlooredTime) + "';"
        cursor.execute(GetCurrentHLV)
        
        CurrentHLV = str(cursor.fetchall())
        CurrentHLV = CurrentHLV.replace("[", "")
        CurrentHLV = CurrentHLV.replace("]", "")
        CurrentHLV = CurrentHLV.replace("(", "")
        CurrentHLV = CurrentHLV.replace(")", "")
        HLV_List = CurrentHLV.split(",")
        
        CurrentHigh = float(HLV_List[0])
        CurrentLow = float(HLV_List[1])
        CurrentVolume = float(HLV_List[2])
        
        if Trade_Price > CurrentHigh:
            CurrentHigh = Trade_Price
        
        if Trade_Price < CurrentLow:
            CurrentLow = Trade_Price
        
        CurrentVolume += Trade_Volume
        
        Query = "UPDATE " + TableName + " SET High = " + str(CurrentHigh) + ", Low = " + str(CurrentLow) + ", Volume = " + str(CurrentVolume) + ", Close = " + str(Trade_Price) + " WHERE CandleTime = '" + str(FlooredTime) + "';"
        print(Query)
        cursor.execute(Query)
                
              

def PrintCandlesticks(Ticker):
    TableName = Ticker.replace("/", "")
    TableName += "Candles"
    
    Query = "SELECT * FROM " + TableName
    cursor.execute(Query)
    pp.pprint(cursor.fetchall())